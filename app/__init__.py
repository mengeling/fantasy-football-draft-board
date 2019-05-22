from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine

import constants as c

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """
    Renders index.html template with draft board table and selected/top player highlighted
    """

    # Retrieve player ID
    id = request.args.get("id", None)
    if id:
        df_player = df[df["id"] == id]
    else:
        df_player = df.iloc[df["rank"].idxmin()]
        id = df_player["id"]

    # Use ID to retrieve image path along with player bio, rankings, and stats
    img_path = "img/{}.jpg".format(id)
    board = df_board.to_html(index=False, escape=False)
    return render_template("index.html", board=board, img_path=img_path)


if __name__ == "__main__":

    # Create DB engine and read draft board table into pandas df
    engine = create_engine(c.DB_ENGINE)
    df = pd.read_sql_query("SELECT * FROM draft_board", con=engine)

    # Create separate draft board df for the HTML table and update headers
    df_board = df[c.DRAFT_BOARD_HEADERS].copy()
    df_board.columns = c.DRAFT_BOARD_DISPLAYED_HEADERS

    # Run the app
    app.run(debug=True)
