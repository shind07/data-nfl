"""
NOTE:
- nflscrapr API takes weeks as a vector, so we just load one season at a time
- for some reason, 2014-reg isn't working
- need to check if season is full
"""
import os
import logging

import docker
import numpy as np
import pandas as pd 


logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

START_SEASON, CURRENT_SEASON = (2011, 2014)
SEASON_TYPES = ('pre', 'reg', 'post')
SEASON_TYPES_ORDER = {game_type: order for order, game_type in enumerate(SEASON_TYPES)}
SEASON_TYPE_WEEK_LENGTHS = ()

DATA_DIR = os.path.join(
    os.path.dirname( # /data-nfl
        os.path.dirname( # /jobs
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
    "volumes" : { # equivalent to -v ${PWD}/data:/app/data  $(NFLSCRAPR_APP_NAME)
        DATA_DIR: {
            "bind": '/app/data',
            'mode': 'rw'
        }   
    },
    "tty": True,
    "stdout": True
}


def extract_current_data():
    """loads games csv into a dataframe.
    
    :return: dataframe if file exists, else None
    :rtype: pandas.DataFrame
    """
    logging.info(f'Loading games data from {GAMES_CSV_PATH}...')

    if not os.path.exists(GAMES_CSV_PATH):
        return None

    df = pd.read_csv(GAMES_CSV_PATH)
    df['season'] = pd.to_numeric(df['season'])
    return df


class DataIntegrityError(Exception):
     pass 


def data_integrity_check(df):
    """Check that the games data is correct.

    3 conditions must be met:
    - there must not be any gaps in the seasons
    - seasons must have all 3 season types (except most recent season)
    - seasons must have semantic ordering of season types (pre -> reg -> post)

    :param df: dataframe of games
    :type df: pandas.DataFrame
    :raises DataIntegrityError: if one of the 3 conditions aren't met
    """
    if df is None:
        logging.warning("Dataframe is empty! No games data recorded.")
        return

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    seasons = df['season'].unique()
    max_season = int(max(seasons))

    expected_seasons = set(range(START_SEASON, max_season + 1))

    if set(seasons) != expected_seasons:
        missing_season = expected_seasons - set(seasons)
        raise DataIntegrityError(f"Most recent season with data is {max_season} but there's no data for {missing_season}!")

    for season in list(seasons):
        season_types = set(df[df['season'] == season]['type'].unique())

        if season != max_season and len(season_types) != 3:
            raise DataIntegrityError(f"{season} is not the max season of {max_season} and only has {len(season_types)} season types")

        elif len(season_types) == 1 and season_types != {'pre'}:
            raise DataIntegrityError(f"There is only 1 season type: {season_types} and its not 'pre'!")

        elif len(season_types) == 2 and season_types != {'pre', 'reg'}:
            raise DataIntegrityError(f"There are 2 season types for {season} and they're not ['pre', 'reg']!")
    

def get_latest_season_and_type(df):
    """gets the latest season and season type in the games data
    
    :param df: games data
    :type df: pandas.DataFrame
    :return: tuple of (latest_season, latest_season_type)
    :rtype: tuple
    """
    if df is None:
        return (None, None)

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    latest_season = df['season'].max()
    season_types = df[df['season'] == latest_season]['type'].unique()
    latest_season_type = get_latest_season_type(list(season_types))
    return latest_season, latest_season_type


def get_latest_season_type(season_types_list):
    """Uses the semantic ordering of season types to get the latest/max
    
    :param season_types_list: list of season types - set or subset of (pre, reg, post)
    :type season_types_list: list or tuple
    :raises ValueError: if season_types_list is not a list or tupe
    :return: the latest season type
    :rtype: str
    """
    if not isinstance(season_types_list, (list, tuple)):
        raise ValueError(f"type of {type(season_types_list)} for season_type_list not list or tuple")

    latest_season_type = season_types_list[0]
    if len(season_types_list) > 1:
        for season_type in season_types_list[1:]:
            if SEASON_TYPES_ORDER[season_type] > SEASON_TYPES_ORDER[latest_season_type]:
                latest_season_type = season_type

    return latest_season_type


def get_complete_season_and_types(df):
    latest_season, latest_season_and_type = get_latest_season_and_type(df)
    prevous_season, previous_season_types = get_previous_season_and_type(latest_season, latest_season_type)

    if previous_season is None and previous_season_types is None:
        return None
    
    return df[
        (df['season'] < previous_season) | (
            (df['season'] == previous_season) &
            (df['type'].isin(previous_season_types)
        )
    ]        


def get_previous_season_and_types(season, season_type):
    if season == START_SEASON and season_type == 'pre':
        prevous_season = previous_season_types = None
    
    else:
        previous_season_types = SEASON_TYPES[:SEASON_TYPES_ORDER[season_type] + 1] if season_type != 'pre' else ('pre')
        previous_season = season if season_type != 'pre' else season - 1
    
    return previous_season, previous_season_type
    

def get_next_season_and_type(season, season_type):
    if season is None and season_type is None:
        return (START_SEASON, SEASON_TYPES[0])

    if not isinstance(season, (np.int64, int)):
        raise ValueError(f"Season is type {type(season)}, it should be type 'int'.")
        
    if season < START_SEASON or season > CURRENT_SEASON:
        raise ValueError(f"Invalid season: {season}, must be in >= {START_SEASON} and <= {CURRENT_SEASON} ")

    if season_type not in SEASON_TYPES:
        raise ValueError(f"Start season type {season_type} not valid.")
    
    if (season, season_type) == (CURRENT_SEASON, 'post'):
        return []

    season_type_order = SEASON_TYPES_ORDER[season_type]
    next_season_type =  SEASON_TYPES[(season_type_order + 1) % len(SEASON_TYPES)]
    next_season = season + 1 if next_season_type == SEASON_TYPES[0] else season
    return next_season, next_season_type


def get_seasons_grid(start_season, start_season_type):
    if start_season not in list(range(START_SEASON, CURRENT_SEASON+1)):
        raise ValueError(f"Start season of {start_season} not valid.")
    
    if start_season_type not in SEASON_TYPES:
        raise ValueError(f"Start season type {start_season_type} not valid.")
    
    initial_season_types = [s for s in SEASON_TYPES if SEASON_TYPES_ORDER[s] >= SEASON_TYPES_ORDER[start_season_type] ]
    grid = [(start_season, season_type) for season_type in initial_season_types]

    if start_season < CURRENT_SEASON:
        for season in range(start_season + 1, CURRENT_SEASON + 1):
            grid += [(season, season_type) for season_type in SEASON_TYPES]

    return grid


def extract_game_data(season, season_type):
    docker_command = f"games --year={season} --type={season_type}" 
    run_docker_container(
        DOCKER_CONTAINER,
        docker_command,
        **DOCKER_CONTAINER_ARGS
    )
    return extract_dumped_data()


def extract_dumped_data():

    if not os.path.exists(DUMP_CSV_PATH):
        raise ValueError(f"Uh oh! {DUMP_CSV_PATH} does not exist!")

    return pd.read_csv(DUMP_CSV_PATH)


def run_docker_container(container, command=None, **kwargs):
    logging.info(f"Running docker container {container} with CMD {command}...")
    client = docker.from_env()
    
    if command:
        kwargs = {"command": command, **kwargs}
    try:
        container = client.containers.run(
            image=container,
            **kwargs
        )

        container_logs = container.decode()
        logging.info("Container output:\n" + container_logs)

    except docker.errors.ContainerError as e:
        logging.error(e)


def load(df):
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    if not os.path.exists(GAMES_CSV_PATH):
        df.to_csv(GAMES_CSV_PATH, index=False) 
    else:
        current_df = extract_current_data()
        updated_df = pd.concat([current_df, df])
        updated_df.drop_duplicates(inplace=True)
        updated_df.to_csv(GAMES_CSV_PATH, index=False)


def main():

    games_data = extract_current_data()
    data_integrity_check(games_data)
    
    games_data = get_complete_season_and_types(games_data)
    latest_season_and_type = get_latest_season_and_type(games_data)
    logging.info(f"Latest season and type: {latest_season_and_type}")

    start_season_and_type = get_next_season_and_type(*latest_season_and_type)
    logging.info(f"Start season and type for batches: {start_season_and_type}")
    batches = get_seasons_grid(*start_season_and_type)

    for batch in batches:
        season, season_type = batch 
        logging.info(f"Extracting data for {season}-{season_type}...")
        data = extract_game_data(season, season_type)
        load(data)


if __name__ == '__main__':
    main()