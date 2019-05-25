import sys
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text

sys.path.append("../data/")

import app_constants as c
import get_data as g

app = Flask(__name__)


def get_top_player_board():
    """
    Select top ranked player and get updated draft board

    :return:
    """

    # Retrieve draft board data and get player ID associated with top ranked player (min rank)
    df = pd.read_sql_query(c.Q_BOARD_ALL, con=engine)
    df_player = df.iloc[[df["rank"].idxmin()]]
    player_id = df_player["id"][0]

    # Convert draft board and player details to HTML
    board = df[c.BOARD_HEADERS].rename(c.RENAMED_BOARD_HEADERS, index=str).to_html(index=False, escape=False)
    player_details = df_player.to_html(index=False, escape=False)
    return board, player_details, player_id


@app.route("/", methods=["GET"])
def index():
    """
    Renders index.html template with draft board table and top available player highlighted
    """

    # Get top available player, draft board, and render them
    board, player_details, player_id = get_top_player_board()
    return render_template("index.html", board=board, player_details=player_details, player_id=int(player_id))


@app.route("/player-details/", methods=["GET"])
def get_player_details():
    """
    Update player picture and details with the selected player
    """

    # Retrieve player ID and player details
    player_id = request.args.get("player_id")
    df_player = pd.read_sql_query(c.Q_BOARD_ID.format(player_id), con=engine)
    player_details = df_player.to_html(index=False, escape=False)
    return jsonify({"player_details": player_details, "player_id": int(player_id)})


@app.route("/get-board-subset/", methods=["GET"])
def get_board_subset():
    """
    Update draft board based on the selected position and/or searched player
    """

    # Filter draft board to players that match the player name search and position selected
    # If all positions are selected, only filter on the player search
    position = request.args.get("position")
    name = request.args.get("player")
    query = c.Q_BOARD_NAME.format(name) if position == "ALL" else c.Q_BOARD_NAME_POSITION.format(position, name)
    df = pd.read_sql_query(text(query), con=engine)

    # Convert draft board to HTML and render it
    board = df[c.BOARD_HEADERS].rename(c.RENAMED_BOARD_HEADERS, index=str).to_html(index=False, escape=False)
    return jsonify({"board": board})


@app.route("/draft-player/", methods=["GET"])
def draft_player():
    """
    Move player from draft board to the drafted board
    """

    # Retrieve player details using player ID
    player_id = request.args.get("player_id")
    df_player = pd.read_sql_query(c.Q_BOARD_ID.format(player_id), con=engine)

    # Write the player to the drafted players table and then remove them from draft board
    df_player.to_sql("drafted_players", con=engine, index=False, if_exists="append")
    engine.execute(c.DELETE_PLAYER_BOARD.format(player_id))

    # Retrieve top player, updated draft board, and pass them back as JSON
    board, player_details, player_id = get_top_player_board()
    return jsonify({"board": board, "player_details": player_details, "player_id": int(player_id)})


@app.route("/get-data/", methods=["GET"])
def get_data():
    """
    Scrape data from fantasy pros, load it into DB, and then render it
    """

    # Get scoring option and pass it into get_dat function to download updated rankings
    scoring_option = request.args.get("scoring_option")
    g.get_data(scoring_option)

    # Retrieve top player, updated draft board, and pass them back as JSON
    board, player_details, player_id = get_top_player_board()
    return jsonify({"board": board, "player_details": player_details, "player_id": int(player_id)})


if __name__ == "__main__":

    # Create DB engine and run the app
    engine = create_engine(c.DB_ENGINE)
    app.run(debug=True)
