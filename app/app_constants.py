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

UPDATE_BOARD = "UPDATE draft_board SET drafted = {} WHERE id = {}"
Q_ALL = "SELECT * FROM draft_board WHERE drafted = {} ORDER BY rank"
Q_ID = "SELECT * FROM draft_board WHERE id = {}"
Q_NAME = "SELECT * FROM draft_board WHERE drafted = {} AND name ILIKE '%{}%' ORDER BY rank"
Q_NAME_POS = "SELECT * FROM draft_board WHERE drafted = {}  AND name ILIKE '%{}%' AND position = '{}' ORDER BY rank"
Q_NAME_TEAM = "SELECT * FROM draft_board WHERE drafted = {} AND name ILIKE '%{}%' AND team = '{}' ORDER BY rank"
Q_NAME_POS_TEAM = """
    SELECT *
    FROM draft_board
    WHERE drafted = {}
    AND name ILIKE '%{}%'
    AND position = '{}'
    AND team = '{}'
    ORDER BY rank
"""

TEAMS = [
    'ARI',
     'ATL',
     'BAL',
     'BUF',
     'CAR',
     'CHI',
     'CIN',
     'CLE',
     'DAL',
     'DEN',
     'DET',
     'FA',
     'GB',
     'HOU',
     'IND',
     'JAC',
     'KC',
     'LAC',
     'LAR',
     'MIA',
     'MIN',
     'NE',
     'NO',
     'NYG',
     'NYJ',
     'OAK',
     'PHI',
     'PIT',
     'SEA',
     'SF',
     'TB',
     'TEN',
     'WAS'
]

