import requests
import sys
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
            for i, td in enumerate(row.find_all("td")):

                # Skip index 1 (empty check box) then get name and team from index 2
                # Get
                # Else if it's not index 1 (empty check box) get value
                if i == 2:
                    name = td.find("a").find("span", class_="full-name").text
                    team = td.find("small", class_="grey").text
                    row_data.extend([name, team])
                elif i == 3:
                    pos_ranking =
                    row_data.append(td.text)
            print(row_data)
            return

        # row_data = []
        #     row_data.append(row.find_all('th')[0].text)
        #     for td in row.find_all('td')[0:20]:
        #         row_data.append(td.text)
        #     row_data[1] = row_data[1].split('*', 1)[0]
        #     rows.append(row_data)


if __name__ == '__main__':

    df_rankings = get_rankings(c.RANKINGS_URL, c.RANKINGS_HEADERS)

