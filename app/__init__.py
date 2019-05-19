from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

import constants as c

app = Flask(__name__)


@app.route('/')
def index():
    """
    Renders index.html template for the main page of the app, using draft board
    """
    return render_template('index.html', data=df.to_html(index=False))


if __name__ == '__main__':

    # Create DB engine and read draft board table into pandas df
    engine = create_engine(c.DB_ENGINE)
    df = pd.read_sql_query("SELECT * FROM draft_board", con=engine)

    # Run the app
    app.run(debug=True)
