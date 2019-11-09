import os

START_SEASON, CURRENT_SEASON = (2011, 2019)
SEASON_TYPES = ('pre', 'reg', 'post')
SEASON_TYPES_ORDER = {game_type: order for order, game_type in enumerate(SEASON_TYPES)}

DATA_DIR = os.path.join(
    os.path.dirname(  # /data-nfl
        os.path.dirname(  # /jobs
            os.path.abspath(__file__)
        )
    ),
    "data"
)
DUMP_CSV_NAME = 'games_dump.csv'
DUMP_CSV_PATH = os.path.join(DATA_DIR, DUMP_CSV_NAME)
GAMES_CSV_PATH = os.path.join(DATA_DIR, "games.csv")

DOCKER_CONTAINER = 'nflscrapr'
DOCKER_CONTAINER_ARGS = {
    "volumes": {  # equivalent to -v ${PWD}/data:/app/data  $(NFLSCRAPR_APP_NAME)
        DATA_DIR: {
            "bind": '/app/data',
            'mode': 'rw'
        }
    },
    "tty": True,
    "stdout": True
}
