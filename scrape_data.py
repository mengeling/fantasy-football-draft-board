import requests
import sys
import re
import pandas as pd
from bs4 import BeautifulSoup

import constants as c


def scrape_rankings(url, headers):
    """
    Get fantasy rankings using the URL provided

    :param html: String, URL for the rankings
    :param headers: List, column headers
    :return: Pandas dataframe
    """

    # Use beautiful soup to retrieve HTML table with rankings
    html = BeautifulSoup(requests.get(url).text, "html.parser")
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
    return pd.DataFrame(rows, columns=headers)


def scrape_previous_stats(url, headers):
    """
    Get stats from the previous year using the URL provided

    :param html: String, URL for the stats
    :param headers: List, column headers
    :return: Pandas dataframe
    """

    # Iterate through each position
    stat_dict = {}
    for k, v in headers.items():

        # Use dictionary keys to retrieve HTML table for each position
        html = BeautifulSoup(requests.get(url.format(k)).text, "html.parser")
        table = html.find("table", id="data").find_all("tbody")[0]

        # Iterate through the rows (tr) in the table
        rows = []
        for row in table.find_all("tr"):

            # Get player ID from the class name and then loop through values in the row
            class_name = row.attrs.get("class")
            row_data = [re.split(r"(\d+)", class_name[0])[1]]
            for i, td in enumerate(row.find_all("td")[:-1]):

                # Get player name from  link and then get rest of the values normally
                if i == 0:
                    name = td.find("a", class_="player-name").text
                    row_data.append(name)
                else:
                    row_data.append(td.text)
            rows.append(row_data)
        stat_dict[k] = pd.DataFrame(rows, columns=v)
    return stat_dict


def scrape_bio(df):
    """
    Go to player's page to get their picture and bio

    :param df: Pandas dataframe with bio URLs
    :return: Pandas dataframe
    """

    # Iterate through df and get picture and bio details
    for i, row in df.iterrows():
        html = BeautifulSoup(requests.get(row["bio_url"]).text, "html.parser")
        if html.find("img", class_="hidden-phone"):
            img_url = "https:" + html.find("img", class_="hidden-phone")["src"]
            html.find("div", class_="clearfix")
        else:
            banner = html.find("ul", class_="pills pills--horizontal desktop-pills")
            stats_url = banner.find_all("li")[2].find("a").attrs.get("href")
            html2 = BeautifulSoup(requests.get(c.BASE_URL + stats_url).text, "html.parser")
            img_url = "https:" + html2.find("div", class_="three columns").find("img")["src"]
        img_path = c.IMG_PATH + row["id"] + ".jpg"
        with open(img_path, "wb") as f:
            f.write(requests.get(img_url).content)




if __name__ == "__main__":

    df_rankings = scrape_rankings(c.RANKINGS_URL, c.RANKINGS_HEADERS)
    df_bio = scrape_bio(df_rankings)
    # stat_dict = scrape_previous_stats(c.STATS_URL, c.STATS_HEADERS)
