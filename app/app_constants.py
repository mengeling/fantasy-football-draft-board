#!/usr/bin/python3
from collections import OrderedDict

HOST_NAME = "ec2-18-233-6-4.compute-1.amazonaws.com"

DB_ENGINE = "postgresql://postgres:postgres@localhost:5432/ffball"

MISSING_PHOTO_URL = "https://images.fantasypros.com/images/photo_missing_square.jpg"

PLAYER_BIO_HEADERS = {
    "id": int,
    "img_url": str,
    "name": str,
    "team": str,
    "position": str,
    "height": str,
    "weight": str,
    "age": int,
    "college": str,
}
PLAYER_BIO_PLACEHOLDERS = {
    "id": "",
    "img_url": MISSING_PHOTO_URL,
    "name": "None",
    "team": "None",
    "position": "None",
    "height": "None",
    "weight": "None",
    "age": "None",
    "college": "None",
}
PLAYER_RANK_HEADERS = OrderedDict([
    ("rank", "Overall"),
    ("position_ranking", "Position"),
    ("best_ranking", "Best"),
    ("worst_ranking", "Worst"),
    ("avg_ranking", "Average"),
    ("std_dev_ranking", "Std Dev"),
    ("avg_draft_pick", "ADP"),
])
PLAYER_STAT_HEADERS = {
    "qb": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("pass_cmp", "PC"),
        ("pass_att", "PA"),
        ("pass_cmp_pct", "PCP"),
        ("pass_yds", "PYD"),
        ("pass_yds_per_att", "YPA"),
        ("pass_td", "PTD"),
        ("pass_int", "PINT"),
        ("rush_att", "RUSH"),
        ("rush_yds", "RUYD"),
        ("rush_td", "RUTD"),
        ("fumbles", "FUM"),
    ]),
    "rb": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("rush_att", "RUSH"),
        ("rush_yds", "RUYD"),
        ("rush_yds_per_att", "YPA"),
        ("rush_20", "20+"),
        ("rush_td", "RUTD"),
        ("receptions", "REC"),
        ("rec_tgt", "RETG"),
        ("rec_yds", "REYD"),
        ("rec_yds_per_rec", "YPR"),
        ("rec_td", "RETD"),
        ("fumbles", "FUM"),
    ]),
    "wr": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("receptions", "REC"),
        ("rec_tgt", "RETG"),
        ("rec_yds", "REYD"),
        ("rec_yds_per_rec", "YPR"),
        ("rec_20", "RE20"),
        ("rec_td", "RETD"),
        ("rush_att", "RUSH"),
        ("rush_yds", "RUYD"),
        ("rush_td", "RUTD"),
        ("fumbles", "FUM"),
    ]),
    "te": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("receptions", "REC"),
        ("rec_tgt", "RETG"),
        ("rec_yds", "REYD"),
        ("rec_yds_per_rec", "YPR"),
        ("rec_20", "RE20"),
        ("rec_td", "RETD"),
        ("rush_att", "RUSH"),
        ("rush_yds", "RUYD"),
        ("rush_td", "RUTD"),
        ("fumbles", "FUM"),
    ]),
    "k": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("field_goals", "FGM"),
        ("fg_att", "FGA"),
        ("fg_pct", "FGP"),
        ("fg_long", "LONG"),
        ("fg_1_19", "1-19"),
        ("fg_20_29", "20-29"),
        ("fg_30_39", "30-39"),
        ("fg_40_49", "40-49"),
        ("fg_50", "50+"),
        ("extra_points", "EPM"),
        ("xp_att", "EPA"),
    ]),
    "dst": OrderedDict([
        ("fantasy_pts", "PTS"),
        ("games", "G"),
        ("sacks", "SACK"),
        ("int", "INT"),
        ("fumbles_recovered", "FR"),
        ("fumbles_forced", "FF"),
        ("def_td", "DTD"),
        ("safeties", "SAFETY"),
        ("special_teams_td", "STTD"),
    ]),
}

BOARD_HEADERS = OrderedDict([
    ("rank", "RANK"),
    ("player", "PLAYER"),
    ("bye_week", "BYE"),
    ("position_ranking", "POS"),
    ("best_ranking", "BEST"),
    ("worst_ranking", "WORST"),
    ("avg_ranking", "AVG"),
    ("std_dev_ranking", "STDEV"),
    ("avg_draft_pick", "ADP"),
    ("fantasy_pts", "PTS"),
    ("pass_cmp", "PAC"),
    ("pass_yds", "PAYD"),
    ("pass_td", "PATD"),
    ("pass_int", "PAINT"),
    ("rush_att", "RUSH"),
    ("rush_yds", "RUYD"),
    ("rush_td", "RUTD"),
    ("receptions", "REC"),
    ("rec_yds", "REYD"),
    ("rec_td", "RETD"),
])

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
