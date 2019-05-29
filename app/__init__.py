import sys
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text

sys.path.append("../data/")

import app_constants as c
import get_data as g

app = Flask(__name__)


def select_top_player_board(username, drafted=0):
    """
    Select top ranked player and get updated draft board

    :param username: String, username used to query draft board
    :param drafted: Binary, 1 if drafted players are shown and 0 if not
    :return: board, pandas dataframe with available or drafted players
    :return: player_details, pandas dataframe with selected player's details
    :return: player_id, integer ID for the selected player
    """

    # Try to get drafted or available draft board and if it fails create empty df
    try:
        df = pd.read_sql_query(c.Q_ALL.format(username, drafted), con=engine)
    except:
        df = pd.DataFrame(columns=c.BOARD_HEADERS)

    # If df doesn't have any rows, create placeholder values
    if df.shape[0] == 0:
        df_player = df
        player_id = None
        img_url = c.MISSING_PHOTO_URL

    # Otherwise use minimum rank to get top ranked player's ID, stats, and image URL
    else:
        df_player = df.iloc[[df["rank"].idxmin()]]
        player_id = int(df_player["id"][0])
        img_url = df_player["img_url"][0]

    # Convert draft board and player details to HTML
    board = df[c.BOARD_HEADERS].rename(columns=c.RENAMED_BOARD_HEADERS, index=str)
    board = board.to_html(index=False, escape=False)
    player_details = df_player.to_html(index=False, escape=False)
    return board, player_details, player_id, img_url


@app.route("/", methods=["GET"])
def login():
    """
    Renders login.html template with draft board table and top available player highlighted
    """

    # Get top available player, draft board, and render them
    return render_template("login.html")


@app.route("/draft-board/<username>", methods=["GET"])
def draft_board(username):
    """
    Renders login.html template with draft board table and top available player highlighted

    :param username: String, username used to select the draft board table
    """

    # Get top available player, draft board, and render them
    board, player_details, player_id, img_url = select_top_player_board(username)
    return render_template(
        "draft_board.html", username=username, board=board, player_details=player_details,
        player_id=player_id, img_url=img_url,
    )


@app.route("/check-if-board-exists/", methods=["GET"])
def check_if_board_exists():
    """
    Check if a draft board exists for the username provided
    """

    username = request.args.get("username")
    username = username.lower().replace(" ", "_")
    exists = pd.read_sql_query(c.CHECK_IF_BOARD_EXISTS.format(username), con=engine).values[0][0]
    return jsonify({"exists": int(exists), "username": username})


@app.route("/player-details/", methods=["GET"])
def get_player_details():
    """
    Update player picture and details with the selected player
    """

    # Retrieve player ID and player details
    username = request.args.get("username")
    player_id = int(request.args.get("player_id"))
    df_player = pd.read_sql_query(c.Q_ID.format(username, player_id), con=engine)
    img_url = df_player["img_url"][0]
    player_details = df_player.to_html(index=False, escape=False)
    return jsonify({"player_details": player_details, "player_id": player_id, "img_url": img_url})


@app.route("/get-player-full-board/", methods=["GET"])
def get_player_full_board():
    """
    Select top ranked player and draft board based on drafted value
    """

    # Use drafted value to get top player, draft board, and pass them back as JSON
    username = request.args.get("username")
    drafted = int(request.args.get("drafted"))
    board, player_details, player_id, img_url = select_top_player_board(username, drafted)
    return jsonify({"board": board, "player_details": player_details, "player_id": player_id, "img_url": img_url})


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
    board = df[c.BOARD_HEADERS].rename(c.RENAMED_BOARD_HEADERS, index=str)
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
    board, player_details, player_id, img_url = select_top_player_board(username, drafted)
    return jsonify({"board": board, "player_details": player_details, "player_id": player_id, "img_url": img_url})


@app.route("/update-data/", methods=["GET"])
def update_data():
    """
    Update data from fantasy pros, load it into DB, and then render it
    """

    # Get username and scoring and use them to download updated rankings
    username = request.args.get("username")
    scoring_option = request.args.get("scoring_option")
    g.get_data(username, scoring_option)

    # Retrieve top player, updated draft board, and pass them back as JSON
    board, player_details, player_id, img_url = select_top_player_board(username)
    return jsonify({"board": board, "player_details": player_details, "player_id": player_id, "img_url": img_url})


@app.route("/get-data/", methods=["GET"])
def get_data():
    """
    Scrape data from fantasy pros for first time, load it into DB, and then render it
    """

    # Get username and scoring, use them to download rankings, and pass username back
    username = request.args.get("username")
    scoring_option = request.args.get("scoring_option")
    g.get_data(username, scoring_option)
    return jsonify({"username": username})


if __name__ == "__main__":

    # Create DB engine and run the app
    engine = create_engine(c.DB_ENGINE)
    app.run(debug=True)
