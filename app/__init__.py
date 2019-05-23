from flask import Flask, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine

import constants as c

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """
    Renders index.html template with draft board table and top available player highlighted
    """

    # Get data and ID associated with the top ranked player
    df_player = df.iloc[[df["rank"].idxmin()]]
    player_id = df_player["id"][0]

    # Get image path, convert player details and draft board to HTML, and render them
    img_path = "img/{}.jpg".format(player_id)
    board = df_board.to_html(index=False, escape=False)
    player_details = df_player.to_html(index=False, escape=False)
    return render_template("index.html", board=board, player_details=player_details, img_path=img_path)


@app.route("/player-details/", methods=["GET"])
def get_player_details():
    """
    Update player picture and details with the selected player
    """

    # Retrieve player ID and player details
    player_id = request.args.get("player_id")
    df_player = pd.DataFrame(df[df["id"] == int(player_id)])

    # Get image path, convert player details and draft board to HTML, and render them
    img_path = "img/{}.jpg".format(player_id)
    player_details = df_player.to_html(index=False, escape=False)
    return jsonify({"img_path": img_path, "player_details": player_details})


if __name__ == "__main__":

    # Create DB engine and read draft board table into pandas df
    engine = create_engine(c.DB_ENGINE)
    df = pd.read_sql_query("SELECT * FROM draft_board", con=engine)

    # Create separate draft board df for the HTML table and update headers
    df_board = df[c.DRAFT_BOARD_HEADERS].copy()
    df_board.columns = c.DRAFT_BOARD_DISPLAYED_HEADERS

    # Run the app
    app.run(debug=True)
