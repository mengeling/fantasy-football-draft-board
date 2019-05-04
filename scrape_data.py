import requests
import sys
import re
import pandas as pd
from bs4 import BeautifulSoup

import constants as c


def get_rankings(url, headers):
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
                    if td.find("small", class_="grey"):
                        name = td.find("a").find("span", class_="full-name").text
                        team = td.find("small", class_="grey").text
                    else:
                        team = td.find("a").find("span", class_="full-name").text
                        name, team = team.replace(")", "").split(" (")
                    row_data.extend([name, team])
                elif i == 3:
                    pos_ranking = re.split(r"(\d+)", td.text)
                    row_data.extend(pos_ranking[:-1])
                elif i == 0 or i > 3:
                    row_data.append(td.text)
            rows.append(row_data)
    return pd.DataFrame(rows, columns=headers)


def get_previous_stats(url, headers):
    """
    Get stats from the previous year using the URL provided

    :param html: String, URL for the rankings
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


if __name__ == "__main__":

    df_rankings = get_rankings(c.RANKINGS_URL, c.RANKINGS_HEADERS)
    stat_dict = get_previous_stats(c.STATS_URL, c.STATS_HEADERS)
