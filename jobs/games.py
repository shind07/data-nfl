import os
import logging

import docker
import pandas as pd 

logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

season_range = (2010, 2019)
game_types = ('pre', 'reg', 'post')

DATA_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "data"
)
DOCKER_CONTAINER = 'nflscrapr'
DOCKER_CONTAINER_ARGS = {
    # -v ${PWD}/data:/app/data  $(NFLSCRAPR_APP_NAME)
    "volumes" : {DATA_DIR: {
        "bind": '/app/data',
        'mode': 'rw'
        }   
    },
    "tty": True,
    "stdout": True
}


def extract():
    logging.info(f'Loading games data from {games_data_path}...')

    games_data_path = os.path.join(
        DATA_DIR,
        "games.csv"
    ) 
    if not os.path.exists(games_data_path):
        backfill()

    return pd.read_csv(games_data_path)


def fetch_latest_week(data):
    latest_season = data['season'].max()
    latest_week = data[data['season'] == latest_season]['week'].max()
    return (latest_season, latest_week)

def backfill():

    date_grid = get_date_grid()

    for season_and_game_type in date_grid[4:10]:
        season, game_type = season_and_game_type
        docker_command = f"games --year={season} --type={game_type}"
        run_docker_container(
            DOCKER_CONTAINER,
            docker_command,
            **DOCKER_CONTAINER_ARGS)


def get_date_grid():
    season_range = (2010, 2020)
    game_types = ('pre', 'reg', 'post')

    grid = []

    for season in range(*season_range):
        grid += [(season, game_type) for game_type in game_types]
    
    return grid

                
def run_docker_container(container, command=None, **kwargs):
    logging.info(f"Running docker container {container}...")
    client = docker.from_env()

    if command:
        kwargs = {"command": command, **kwargs}
    
    
    container = client.containers.run(
        image=container,
        **kwargs)
    
    container_logs = container.decode()
    logging.info("Container output:\n" + container_logs)

def main():
    
    # data = extract()
    backfill()

if __name__ == '__main__':
    main()