import requests
import os
import sys
import re
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

import constants as c


def login_fpros(url, user, pswd):
    """
    Use username and password to log into fantasy pros

    :param url: String, URL to the login page
    :param user: String, fantasy pros username
    :param pswd: String, fantasy pros password
    :return: Object, logged in request session
    """

    session = requests.session()
    html = BeautifulSoup(session.get(url).text, "html.parser")
    token = html.find("input", {"name": "csrfmiddlewaretoken"}).attrs.get("value")
    payload = {"username": user, "password": pswd, "csrfmiddlewaretoken": token}
    session.post(url, data=payload, headers=dict(referer=url))
    return session


def download_photo(img_url, file_path):
    """
    Use image URL to download player's photo and dump it in the data directory.
    If it fails with 403 error, save the missing person photo.

    :param img_url: String, URL to download the photo
    :param file_path: String, file path to dump the photo
    """

    response = requests.get(img_url)
    if response.status_code == 403:
        response = requests.get(c.MISSING_PHOTO_URL)
    with open(file_path, "wb") as f:
        f.write(response.content)


def load_data(df, table_name, engine):
    """
    Write data to CSV and then load it into the DB

    :param df: Pandas dataframe
    :param table_name: String, name of the table
    :param engine: Object, DB connection
    :return:
    """

    # Write df to CSV, load it again to infer data types, and write it to table
    df.to_csv(table_name + ".csv", index=False)
    df = pd.read_csv(table_name + ".csv")
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def create_stats_all(headers_dict, headers, engine):
    """
    Create all stats table that combines position stats tables

    :param headers_dict: Dictionary, positions are keys and values are column headers for that position
    :param headers: List, column headers for new table
    :param engine: Object, DB connection
    """

    # Loop through position stats, retrieve stat columns (add zeros if missing), and concatenate them together
    stats_lst = []
    for k in headers_dict.keys():
        df_stats = pd.read_sql_query("SELECT * FROM stats_{}".format(k), con=engine)
        df_standardized_stats = pd.DataFrame()
        for col in headers:
            df_standardized_stats[col] = df_stats[col] if col in df_stats.columns else 0
        stats_lst.append(df_standardized_stats)
    df = pd.concat(stats_lst)

    # To drop duplicates, return row with most points scored for each player and then write to DB
    df = df.sort_values("fantasy_pts", ascending=False)
    df = df.groupby("id", as_index=False).first()
    load_data(df, "stats_all", engine)


def create_draft_board(query, engine):
    """
    Create draft board table by combining rankings, stats, and bios

    :param query: String, SQL query that joins tables
    :param engine: Object, DB connection
    """

    # Retrieve data from rankings, stats, and bios, add player column, and save draft board in DB and as CSV
    df = pd.read_sql_query(query, engine)
    df["player"] = "<span class='fake-link' id='" + df["id"].astype(str) + "'>" + df["name"] \
                   + ", " + df["team"] + ", " + df["position"] + "</span>"
    load_data(df, "draft_board", engine)


def scrape_rankings(session, url, headers, engine):
    """
    Get fantasy rankings using the URL provided

    :param session: Object, logged in request session
    :param url: String, URL for the rankings
    :param headers: List, column headers
    :param engine: Object, DB connection
    :return: Pandas dataframe
    """

    # Use beautiful soup to retrieve HTML table with rankings
    html = BeautifulSoup(session.get(url).text, "html.parser")
    table = html.find("table", id="rank-data").find_all("tbody")[0]

    # Iterate through the rows (tr) in the table
    rows = []
    for row in table.find_all("tr"):

        # Ignore rows that don't have players in them (class = "player-row")
        if "player-row" in row.attrs.get("class"):

            # Add player ID to an empty list and then loop through row values
            row_data = [row.attrs.get("data-id")]
            for i, td in enumerate(row.find_all("td")[:-1]):

                # Skip index 1 (empty check box) and get name and team from index 2
                # Split position and position ranking from index 3 and then rest are just text
                if i == 2:
                    player = td.find("a")
                    bio_url = c.BASE_URL + player.attrs.get("href")
                    name = player.find("span", class_="full-name").text
                    if td.find("small", class_="grey"):
                        team = td.find("small", class_="grey").text
                    else:
                        name, team = name.replace(")", "").split(" (")
                    row_data.extend([name, bio_url, team])
                elif i == 3:
                    pos_ranking = re.split(r"(\d+)", td.text)
                    row_data.extend(pos_ranking[:-1])
                elif i == 0 or i > 3:
                    row_data.append(td.text)
            rows.append(row_data)
    df = pd.DataFrame(rows, columns=headers)
    load_data(df, "rankings", engine)
    return df


def scrape_previous_stats(url, headers_dict, engine):
    """
    Get stats from the previous year using the URL provided

    :param url: String, URL for the stats
    :param headers_dict: Dictionary, positions are keys and values are column headers for that position
    :param engine: Object, DB connection
    :return: Dictionary, keys are position strings and values are stat dfs
    """

    # Iterate through each position to retrieve stats
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
            for i, td in enumerate(row.find_all("td")[:-1]):
                if i > 0:
                    row_data.append(td.text)
            rows.append(row_data)

        # Create dataframe for the position, add position, and add df to dictionary
        df = pd.DataFrame(rows, columns=v)
        df["position"] = k.upper()
        load_data(df, "stats_" + k, engine)


def scrape_bios(df, headers, engine):
    """
    Go to player's page to get their picture and bio

    :param df: Pandas dataframe with bio URLs
    :param headers: List, column headers
    :param engine: Object, DB connection
    :return: Pandas dataframe
    """

    # Iterate through player rankings and get bio details and picture
    rows = []
    for i, row in df.iterrows():

        # If it's a player get bio details in the clearfix div
        html = BeautifulSoup(requests.get(row["bio_url"]).text, "html.parser")
        if html.find("img", class_="hidden-phone"):
            bio_div = html.find("div", class_="clearfix")
            bio_details = bio_div.find_all("span", class_="bio-detail")

            # Use semi-colon to split detail type and value and put in dict (e.g. Weight: 230lbs)
            bio_details_dict = {detail.text.split(": ")[0]: detail.text.split(": ")[1] for detail in bio_details}

            # Create list with ID then look up values from dict for other columns. If not in dict assign null
            row_data = [row["id"]]
            for header in headers[1:]:
                if header.title() in bio_details_dict.keys():
                    row_data.append(bio_details_dict[header.title()])
                else:
                    row_data.append(None)

            # Add details to list and get image URL
            rows.append(row_data)
            img_url = "https:" + html.find("img", class_="hidden-phone")["src"]

        # If it's a team go to Team Stats tab in the top banner and get team logo
        else:
            banner = html.find("ul", class_="pills pills--horizontal desktop-pills")
            stats_url = banner.find_all("li")[2].find("a").attrs.get("href")
            html = BeautifulSoup(requests.get(c.BASE_URL + stats_url).text, "html.parser")
            img_url = "https:" + html.find("div", class_="three columns").find("img")["src"]

        # Retrieve and dump photo and then wait a second or two
        download_photo(img_url, c.IMG_PATH + row["id"] + ".jpg")
        time.sleep(np.random.uniform(0, 2, 1)[0])
    df = pd.DataFrame(rows, columns=headers)
    load_data(df, "bios", engine)


if __name__ == "__main__":

    # Get URLs for fantasy pros rankings and stats using scoring settings passed into script
    if sys.argv[1] == "standard":
        rankings_url = c.RANKINGS_URL.format("consensus")
        stats_url = c.STATS_URL
    elif sys.argv[1] == "ppr":
        rankings_url = c.RANKINGS_URL.format("ppr")
        stats_url = c.STATS_URL + "?scoring=PPR"
    else:
        rankings_url = c.RANKINGS_URL.format("half-point-ppr")
        stats_url = c.STATS_URL + "?scoring=HALF"

    # Create session that's logged into fantasy pros and create DB engine object
    session = login_fpros(c.LOGIN_URL, os.environ["FPROS_USER"], os.environ["FPROS_PSWD"])
    engine = create_engine(c.DB_ENGINE)

    # Scrape rankings, stats, and bios and load them into the DB
    df_rankings = scrape_rankings(session, rankings_url, c.RANKINGS_HEADERS, engine)
    scrape_bios(df_rankings, c.BIO_HEADERS, engine)
    scrape_previous_stats(stats_url, c.STATS_HEADERS, engine)

    # Create stats_all and consolidate rankings, stats, and bios in draft board and then create empty drafted_players
    create_stats_all(c.STATS_HEADERS, c.STATS_ALL_HEADERS, engine)
    create_draft_board(c.DRAFT_BOARD_QUERY, engine)
    engine.execute(c.CREATE_DRAFTED_PLAYERS)
