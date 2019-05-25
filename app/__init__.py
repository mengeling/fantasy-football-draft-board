from flask import Flask, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, text

import constants as c

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """
    Renders index.html template with draft board table and top available player highlighted
    """

    # Retrieve draft board data and get player ID associated with top ranked player (min rank)
    df = pd.read_sql_query(c.QUERY_BOARD_ALL, con=engine)
    df_player = df.iloc[[df["rank"].idxmin()]]
    player_id = df_player["id"][0]

    # Get image path, convert player details and draft board to HTML, and render them
    img_path = "img/{}.jpg".format(player_id)
    board = df[c.BOARD_HEADERS].rename(c.RENAMED_BOARD_HEADERS, index=str).to_html(index=False, escape=False)
    player_details = df_player.to_html(index=False, escape=False)
    return render_template("index.html", board=board, player_details=player_details, img_path=img_path)


@app.route("/player-details/", methods=["GET"])
def get_player_details():
    """
    Update player picture and details with the selected player
    """

    # Retrieve player ID and player details
    player_id = request.args.get("player_id")
    df_player = pd.read_sql_query(c.QUERY_BOARD_ID.format(player_id), con=engine)

    # Get image path, convert player details and draft board to HTML, and render them
    img_path = "img/{}.jpg".format(player_id)
    player_details = df_player.to_html(index=False, escape=False)
    return jsonify({"img_path": img_path, "player_details": player_details})


@app.route("/get-board-subset/", methods=["GET"])
def get_board_subset():
    """
    Update draft board based on the selected position and/or searched player
    """

    # Filter draft board to players that match the player name search and position selected
    # If all positions are selected, only filter on the player search
    position = request.args.get("position")
    player_name = request.args.get("player")
    if position == "ALL":
        df = pd.read_sql_query(text(c.QUERY_BOARD_NAME.format(player_name)), con=engine)
    else:
        df = pd.read_sql_query(text(c.QUERY_BOARD_NAME_POSITION.format(position, player_name)), con=engine)

    # Convert draft board to HTML and render it
    board = df[c.BOARD_HEADERS].rename(c.RENAMED_BOARD_HEADERS, index=str).to_html(index=False, escape=False)
    return jsonify({"board": board})


if __name__ == "__main__":

    # Create DB engine and run the app
    engine = create_engine(c.DB_ENGINE)
    app.run(debug=True)
