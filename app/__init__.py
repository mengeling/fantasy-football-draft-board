import sys
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text

pd.set_option("display.max_colwidth", -1)
sys.path.append("../data/")

import app_constants as c
import get_data as g

app = Flask(__name__)


def parse_player_details(df_player):
    """
    Parse all of the individual components of the player details

    :param df_player: Pandas dataframe, selected player's details
    :return bio_dict, df_rank, and df_stats for the specified player
    """

    # Loop through bio columns and add the value to player's dictionary
    bio = {}
    for col, dtype in c.PLAYER_BIO_HEADERS.items():
        bio[col] = dtype(df_player[col][0])

    # Get ranking data and rename columns for display
    rank_cols = list(c.PLAYER_RANK_HEADERS.keys())
    rankings = df_player[rank_cols].rename(columns=c.PLAYER_RANK_HEADERS, index=str)

    # Use player's position to get position-specific stats
    position = bio["position"].lower()
    stat_cols = list(c.PLAYER_STAT_HEADERS[position].keys())
    stats = df_player[stat_cols].rename(columns=c.PLAYER_STAT_HEADERS[position], index=str)
    return bio, rankings, stats


def select_top_player_board(username, drafted=0):
    """
    Select top ranked player and get updated draft board

    :param username: String, username used to query draft board
    :param drafted: Binary, 1 if drafted players are shown and 0 if not
    :return: player_shared_dict, player_position_dict, and draft board df
    """

    # Try to get draft board (drafted or available) and player details for top player
    try:

        # Query draft board and use minimum rank to get top player
        df = pd.read_sql_query(c.Q_ALL.format(username, drafted), con=engine)
        df_player = df.iloc[[df["rank"].idxmin()]]

        # Parse player data into bio dict and ranking and stat dfs and then select draft board columns
        player_bio, player_rankings, player_stats = parse_player_details(df_player)
        board_cols = list(c.BOARD_HEADERS.keys())
        board = df[board_cols].rename(columns=c.BOARD_HEADERS, index=str)

    # If it fails, create placeholder data
    except:
        player_bio = {}
        rank_cols = list(c.PLAYER_RANK_HEADERS.keys())
        stat_cols = list(c.PLAYER_STAT_HEADERS["qb"].keys())
        board_cols = list(c.BOARD_HEADERS.keys())
        player_rankings = pd.DataFrame(columns=rank_cols)
        player_stats = pd.DataFrame(columns=stat_cols)
        board = pd.DataFrame(columns=board_cols).rename(columns=c.BOARD_HEADERS, index=str)

    # Convert player rankings, player stats, and draft board to HTML
    player_rankings = player_rankings.to_html(index=False, escape=False)
    player_stats = player_stats.to_html(index=False, escape=False)
    board = board.to_html(index=False, escape=False)
    return player_bio, player_rankings, player_stats, board


@app.route("/", methods=["GET"])
def index():
    """
    Renders index.html template with placeholder values until data is retrieved
    """

    # Create placeholders
    bio, rankings, stats, board = select_top_player_board(username="mike")
    return render_template("index.html", bio=bio, rankings=rankings, stats=stats, board=board, **bio)


@app.route("/check-if-board-exists/", methods=["GET"])
def check_if_board_exists():
    """
    Check if a draft board exists for the username provided
    """

    username = request.args.get("username")
    username = username.lower().replace(" ", "_")
    exists = pd.read_sql_query(c.CHECK_IF_BOARD_EXISTS.format(username), con=engine).values[0][0]
    return jsonify({"exists": int(exists), "username": username})


@app.route("/get-data/", methods=["GET"])
def get_data():
    """
    Add draft board table and top available player to index.html
    """

    # Get top available player, draft board, and render them
    username = request.args.get("username")
    player_shared, player_pos, board = select_top_player_board(username)
    return jsonify({"player_shared": player_shared, "player_pos": player_pos, "board": board})


@app.route("/get-player-details/", methods=["GET"])
def get_player_details():
    """
    Update player picture and details with the selected player
    """

    # Retrieve player ID and player details
    username = request.args.get("username")
    player_id = int(request.args.get("player_id"))
    df_player = pd.read_sql_query(c.Q_ID.format(username, player_id), con=engine)
    player_dict = parse_player_details(df_player)
    return jsonify({"player_dict": player_dict})


@app.route("/get-drafted-board/", methods=["GET"])
def get_drafted_board():
    """
    Select top ranked player and draft board based on drafted value
    """

    # Use drafted value to get top player, draft board, and pass them back as JSON
    username = request.args.get("username")
    drafted = int(request.args.get("drafted"))
    player_dict, board = select_top_player_board(username, drafted)
    return jsonify({"player_dict": player_dict, "board": board})


@app.route("/get-board-subset/", methods=["GET"])
def get_board_subset():
    """
    Update draft board based on the selected position, team, and/or searched player
    """

    # Filter draft board to players that match the drafted status, name search, team, and position selections
    username = request.args.get("username")
    drafted = int(request.args.get("drafted"))
    position = request.args.get("position")
    team = request.args.get("team")
    name = request.args.get("name")
    if position == "ALL" and team == "ALL":
        q = c.Q_NAME.format(username, drafted, name)
    elif position != "ALL" and team == "ALL":
        q = c.Q_NAME_POS.format(username, drafted, name, position)
    elif position == "ALL" and team != "ALL":
        q = c.Q_NAME_TEAM.format(username, drafted, name, team)
    else:
        q = c.Q_NAME_POS_TEAM.format(username, drafted, name, position, team)
    df = pd.read_sql_query(text(q), con=engine)

    # Convert draft board to HTML and render it
    board = df[c.BOARD_HEADERS.keys].rename(columns=c.BOARD_HEADERS, index=str)
    board = board.to_html(index=False, escape=False)
    return jsonify({"board": board})


@app.route("/draft-undraft-player/", methods=["GET"])
def draft_undraft_player():
    """
    Move selected player from draft board to the drafted board
    """

    # Retrieve player details using player ID and flip drafted value for the player
    username = request.args.get("username")
    drafted = int(request.args.get("drafted"))
    updated_drafted = 1 if drafted == 0 else 0
    player_id = request.args.get("player_id")
    engine.execute(c.UPDATE_BOARD.format(username, updated_drafted, player_id))

    # Retrieve top player, updated draft board, and pass them back as JSON
    player_dict, board = select_top_player_board(username, drafted)
    return jsonify({"player_dict": player_dict, "board": board})


@app.route("/download-data/", methods=["GET"])
def download_data():
    """
    Scrape data from fantasy pros, load it into DB, and then retrieve data
    """

    # Get username and scoring and use them to download updated rankings
    username = request.args.get("username")
    scoring_option = request.args.get("scoring_option")
    g.get_data(username, scoring_option)

    # Retrieve top player, updated draft board, and pass them back as JSON
    player_dict, board = select_top_player_board(username)
    return jsonify({"player_dict": player_dict, "board": board})


if __name__ == "__main__":

    # Create DB engine and run the app
    engine = create_engine(c.DB_ENGINE)
    app.run(debug=True)
