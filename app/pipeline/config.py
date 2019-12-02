import os

root_dir = os.path.dirname(  # /app
    os.path.dirname(  # /pipeline
        os.path.abspath(__file__)
    )
)

START_SEASON, CURRENT_SEASON = (2011, 2019)
SEASON_TYPES = ('pre', 'reg', 'post')
SEASON_TYPES_ORDER = {game_type: order for order, game_type in enumerate(SEASON_TYPES)}
DATA_DIR = os.path.join(root_dir, "data")
GAMES_DUMP_CSV_NAME = 'games_dump.csv'
GAMES_DUMP_CSV_PATH = os.path.join(DATA_DIR, GAMES_DUMP_CSV_NAME)
GAMES_CSV_PATH = os.path.join(DATA_DIR, "games.csv")
NFLSCRAPR_JOBS_PATH = os.path.join(root_dir, "nflscrapr")
