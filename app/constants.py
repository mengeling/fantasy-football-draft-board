IMG_PATH = "../app/static/img/"

DB_ENGINE = "postgresql://mengeling:mengeling@localhost:5432/ffball"

BOARD_HEADERS = [
    "rank",
    "player",
    "bye_week",
    "position_ranking",
    "best_ranking",
    "worst_ranking",
    "avg_ranking",
    "std_dev_ranking",
    "avg_draft_pick",
    "fantasy_pts",
    "pass_cmp",
    "pass_att",
    "pass_yds",
    "pass_td",
    "pass_int",
    "rush_att",
    "rush_yds",
    "rush_td",
    "receptions",
    "rec_yds",
    "rec_td"
]

RENAMED_BOARD_HEADERS = {
    "rank": "RANK",
    "player": "PLAYER",
    "bye_week": "BYE",
    "position_ranking": "POS",
    "best_ranking": "BEST",
    "worst_ranking": "WORST",
    "avg_ranking": "AVG",
    "std_dev_ranking": "STDEV",
    "avg_draft_pick": "ADP",
    "fantasy_pts": "PTS",
    "pass_cmp": "COM",
    "pass_att": "ATT",
    "pass_yds": "PAYD",
    "pass_td": "PATD",
    "pass_int": "PAINT",
    "rush_att": "RUSH",
    "rush_yds": "RUYD",
    "rush_td": "RUTD",
    "receptions": "REC",
    "rec_yds": "REYD",
    "rec_td": "RETD"
}

QUERY_BOARD_ALL = "SELECT * FROM draft_board"
QUERY_BOARD_ID = "SELECT * FROM draft_board WHERE id = {}"
QUERY_BOARD_NAME = "SELECT * FROM draft_board WHERE name ILIKE '%{}%'"
QUERY_BOARD_NAME_POSITION = "SELECT * FROM draft_board WHERE position = '{}' AND name ILIKE '%{}%'"
DELETE_PLAYER_BOARD = "DELETE FROM draft_board WHERE id = {}"

