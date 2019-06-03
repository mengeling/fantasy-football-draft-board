DB_ENGINE = "postgresql://mengeling:mengeling@localhost:5432/ffball"

MISSING_PHOTO_URL = "https://images.fantasypros.com/images/photo_missing_square.jpg"

BIO_HEADERS = ["bye_week", "height", "weight", "age", "college"]
SHARED_STAT_HEADERS = [
    "rank",
    "position_ranking",
    "best_ranking",
    "worst_ranking",
    "avg_ranking",
    "std_dev_ranking",
    "avg_draft_pick",
    "fantasy_pts",
]
POS_STAT_HEADERS = {
    "qb": [
        "id",
        "pass_cmp",
        "pass_att",
        "pass_cmp_pct",
        "pass_yds",
        "pass_yds_per_att",
        "pass_td",
        "pass_int",
        "pass_sacks",
        "rush_att",
        "rush_yds",
        "rush_td",
        "fumbles",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
    "rb": [
        "id",
        "rush_att",
        "rush_yds",
        "rush_yds_per_att",
        "rush_long",
        "rush_20",
        "rush_td",
        "receptions",
        "rec_tgt",
        "rec_yds",
        "rec_yds_per_rec",
        "rec_td",
        "fumbles",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
    "wr": [
        "id",
        "receptions",
        "rec_tgt",
        "rec_yds",
        "rec_yds_per_rec",
        "rec_long",
        "rec_20",
        "rec_td",
        "rush_att",
        "rush_yds",
        "rush_td",
        "fumbles",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
    "te": [
        "id",
        "receptions",
        "rec_tgt",
        "rec_yds",
        "rec_yds_per_rec",
        "rec_long",
        "rec_20",
        "rec_td",
        "rush_att",
        "rush_yds",
        "rush_td",
        "fumbles",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
    "k": [
        "id",
        "field_goals",
        "fg_att",
        "fg_pct",
        "fg_long",
        "fg_1_19",
        "fg_20_29",
        "fg_30_39",
        "fg_40_49",
        "fg_50",
        "extra_points",
        "xp_att",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
    "dst": [
        "id",
        "sacks",
        "int",
        "fumbles_recovered",
        "fumbles_forced",
        "def_td",
        "safeties",
        "special_teams_td",
        "games",
        "fantasy_pts",
        "fantasy_pts_per_game",
    ],
}
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
    "pass_yds",
    "pass_td",
    "pass_int",
    "rush_att",
    "rush_yds",
    "rush_td",
    "receptions",
    "rec_yds",
    "rec_td",
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
    "pass_cmp": "PAC",
    "pass_yds": "PAYD",
    "pass_td": "PATD",
    "pass_int": "PAINT",
    "rush_att": "RUSH",
    "rush_yds": "RUYD",
    "rush_td": "RUTD",
    "receptions": "REC",
    "rec_yds": "REYD",
    "rec_td": "RETD",
}

CHECK_IF_BOARD_EXISTS = """
SELECT EXISTS (
    SELECT *
    FROM information_schema.tables
    WHERE table_name = 'draft_board_{}'
)
"""
UPDATE_BOARD = "UPDATE draft_board_{} SET drafted = {} WHERE id = {}"
Q_ALL = "SELECT * FROM draft_board_{} WHERE drafted = {} ORDER BY rank"
Q_ID = "SELECT * FROM draft_board_{} WHERE id = {}"
Q_NAME = "SELECT * FROM draft_board_{} WHERE drafted = {} AND name ILIKE '%{}%' ORDER BY rank"
Q_NAME_POS = "SELECT * FROM draft_board_{} WHERE drafted = {}  AND name ILIKE '%{}%' AND position = '{}' ORDER BY rank"
Q_NAME_TEAM = "SELECT * FROM draft_board_{} WHERE drafted = {} AND name ILIKE '%{}%' AND team = '{}' ORDER BY rank"
Q_NAME_POS_TEAM = """
    SELECT *
    FROM draft_board_{}
    WHERE drafted = {}
    AND name ILIKE '%{}%'
    AND position = '{}'
    AND team = '{}'
    ORDER BY rank
"""
