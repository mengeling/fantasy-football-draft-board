
#!/usr/bin/python3
import requests
import sys
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import create_engine
from datetime import datetime

sys.path.append("/var/www/ffball/fantasy-football-draft-board/data/")
import data_constants as c


def create_draft_board(engine, username, df_rankings, df_stats):
    """
    Create draft board table by combining rankings, stats, and bios

    :param engine: Object, DB connection
    :param username: String, username that's included in the table name
    :param df_rankings: Pandas dataframe, player rankings
    :param df_stats: Pandas dataframe, player stats
    """

    # Left join rankings dataframe to the stats dataframe
    df_rankings = df_rankings.set_index("id")
    df_stats = df_stats.set_index("id")
    df = df_rankings.join(df_stats, how="left").reset_index()

    # Fill nulls and non-numeric values with zeros
    stat_cols = df_stats.columns
    df[stat_cols] = df[stat_cols].fillna(0)
    for col in c.FILL_NULL_COLS:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r"[^0-9]", "")).fillna(0).astype(int)

    # Create drafted column with zeros since no one's been drafted and create timestamp column
    df["drafted"] = np.zeros(df.shape[0])
    df["created_timestamp"] = datetime.now()

    # Create styled player column for app that combines name, team, and position columns
    df["player"] = (
        "<span class='fake-link' id='"
        + df["id"].astype(str)
        + "'>"
        + df["name"]
        + "</span>"
        + ", "
        + df["team"]
        + ", "
        + df["position"]
    )

    # Create draft board table and then load the dataframe into it
    engine.execute(c.CREATE_DRAFT_BOARD.format(username, username))
    df.to_sql("draft_board_" + username, con=engine, index=False, if_exists="append")


def create_stats_all(dict_stats, headers):
    """
    Create all stats table that combines position stats tables

    :param dict_stats: Dictionary, positions are keys and values are pandas dfs with stats for that position
    :param headers: List, column headers for combined stats data
    :return: Pandas dataframe, combined stats data
    """

    # Loop through position stats, retrieve stat columns (add zeros if missing), and concatenate them together
    stats_df_lst = []
    for k, df_pos_stats in dict_stats.items():
        df_standardized_stats = pd.DataFrame()
        for col in headers:
            df_standardized_stats[col] = df_pos_stats[col] if col in df_pos_stats.columns else 0
        stats_df_lst.append(df_standardized_stats)
    df = pd.concat(stats_df_lst)

    # To drop duplicates (players with multiple positions) keep rows with most points scored for each ID
    df = df.sort_values("fantasy_pts", ascending=False)
    return df.groupby("id", as_index=False).first()


def scrape_stats(url, headers_dict, stats_all_headers):
    """
    Get stats from the previous year using the URL provided

    :param url: String, URL for the stats
    :param headers_dict: Dictionary, positions are keys and values are column headers for that position
    :param stats_all_headers: List, column headers for combined stats data
    :return: Pandas dataframe, combined stats data
    """

    # Iterate through each position to retrieve stats and store them in dictionary
    dict_stats = {}
    for k, v in headers_dict.items():

        # Use dictionary keys to retrieve HTML table for each position
        html = BeautifulSoup(requests.get(url.format(k)).text, "html.parser")
        table = html.find("table", id="data").find_all("tbody")[0]

        # Iterate through the rows (tr) in the table
        rows = []
        for row in table.find_all("tr"):

            # Get player ID from the class name and then loop through values in the row
            # Skip player name in index 0 and then get stats
            class_name = row.attrs.get("class")
            row_data = [re.split(r"(\d+)", class_name[0])[1]]
            for i, td in enumerate(row.find_all("td")[2:-1]):
                row_data.append(td.text)
            rows.append(row_data)

        # Create dataframe for the position and add it to the dictionary
        df = pd.DataFrame(rows, columns=v)
        dict_stats[k] = df

    # Combine each position's stats into one table and return combined df
    return create_stats_all(dict_stats, stats_all_headers)


def scrape_bio(row_data, bio_headers):
    """
    Go to player's page to get their picture and bio

    :param row_data: List, player IDs and rankings
    :param bio_headers: List, column headers for bio data
    :return: row_data list with new bio columns
    """

    # Get HTML for the bio page
    bio_url = row_data[2]
    html = BeautifulSoup(requests.get(bio_url).text, "html.parser")

    # If there's a picture elemenet it's a player's bio. Get their image and bio details
    try:
        img_url = html.findAll("picture")[0].find("img")["src"]
        row_data.append(img_url)

        # Get bio details in the clearfix div
        bio_div = html.find("div", class_="clearfix")
        bio_details = bio_div.find_all("span", class_="bio-detail")

        # Use colon to split detail type and value and put in dict (e.g. Weight: 230lbs)
        bio_details_dict = {detail.text.split(": ")[0]: detail.text.split(": ")[1] for detail in bio_details}

        # Loop through bio details columns after ID and photo_url. Add dict value if available or null otherwise
        for header in bio_headers:
            if header in bio_details_dict.keys():
                row_data.append(bio_details_dict[header])
            else:
                row_data.append(None)

    # Otherwise it's a team or bad link so leave everything null
    except:
        row_data.extend([None, None, None, None, None])
    return row_data


def scrape_rankings(driver, url, ranking_headers, bio_headers):
    """
    Get fantasy rankings using the URL provided

    :param driver: Selenium driver
    :param url: String, URL for the rankings
    :param ranking_headers: List, column headers for ranking data
    :param bio_headers: List, column headers for bio data
    :return: Pandas dataframe, ranking data
    """

    # Use Selenium to load first n rows of table and scroll down to the nth row to load the rest of the rows
    driver.get(url)
    table = driver.find_element_by_xpath("//*/table[@id='ranking-table']")
    last_row = table.find_elements_by_xpath("tbody/tr[@class='player-row']")[-1]
    driver.execute_script("arguments[0].scrollIntoView();", last_row)
    selenium_rows = table.find_elements_by_xpath("tbody/tr[@class='player-row']")

    # Iterate through the rows (tr) in the table
    rows = []
    for selenium_row in selenium_rows:

        # Loop through row values to get player data
        row = BeautifulSoup(selenium_row.get_attribute("innerHTML"), "html.parser")
        row_data = []
        for i, td in enumerate(row.find_all("td")[:5]):

            # Get overall ranking from index 0 and skip index 1 (empty check box)
            if i == 0:
                row_data.append(td.text)

            # Get bio URL, name, and team from index 2
            elif i == 2:
                player_id = td.find("div").attrs.get("data-player")
                bio_url = td.find("a").attrs.get("href")
                name = td.find("a").text
                team = td.find("span").text[1:-1]
                row_data.extend([player_id, bio_url, name, team])

            # Split position and position ranking from index 3
            elif i == 3:
                pos_ranking = re.split(r"(\d+)", td.text)
                row_data.extend(pos_ranking[:-1])

            # Get bye week from index 4
            elif i == 4:
                row_data.append(td.text)

        # Use scrape_bio function to append player photo URL and bio details to list
        row_data_with_bio = scrape_bio(row_data, bio_headers)
        rows.append(row_data_with_bio)
    return pd.DataFrame(rows, columns=ranking_headers)


def get_data(username, scoring_option):
    """
    Scrape data from fantasy pros and load it into DB

    :param username: String, username that's included in the table name
    :param scoring_option: String, selected scoring option
    """

    # Create Selenium driver used to parse HTML
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(c.DRIVER_PATH, options=options)
    driver.set_page_load_timeout(10)

    # Based on the scoring option, get the fantasy pros URLs to the rankings and stats pages
    if scoring_option == "standard":
        rankings_url = c.RANKINGS_URL.format("consensus")
        stats_url = c.STATS_URL
    elif scoring_option == "ppr":
        rankings_url = c.RANKINGS_URL.format("ppr")
        stats_url = c.STATS_URL + "?scoring=PPR"
    else:
        rankings_url = c.RANKINGS_URL.format("half-point-ppr")
        stats_url = c.STATS_URL + "?scoring=HALF"

    # Scrape rankings and stats
    df_rankings = scrape_rankings(driver, rankings_url, c.RANKINGS_HEADERS, c.BIO_HEADERS)
    driver.quit()
    df_stats = scrape_stats(stats_url, c.STATS_HEADERS, c.STATS_ALL_HEADERS)

    # Create DB connection and then write combined rankings, bios, and stats to DB
    engine = create_engine(c.DB_ENGINE)
    create_draft_board(engine, username, df_rankings, df_stats)


if __name__ == "__main__":

    # If executed as script pass username and scoring option into get_data function
    username, scoring_option = sys.argv[1:3]
    get_data(username, scoring_option)
