"""
LOGIC:
- find the latest season in the data with incomplete games (state_of_game != POST)
- drop this data and reload it

NOTE:
- nflscrapr API takes weeks as a vector, so we just load one season at a time
- for some reason, 2014-reg isn't working
- need to check if season is full

TODO:
- complete tests
- set up linter
- set up cloud container repo
    - start with dockerhub, then ECR
- set up travisCI
- put nflscrapr in its own repo
"""
import os
import logging

import docker
import numpy as np
import pandas as pd 

from . import config

logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


def extract_current_data():
    """Loads games csv into a dataframe.
    
    :return: dataframe if file exists, else None
    :rtype: pandas.DataFrame
    """
    logging.info(f'Loading games data from {config.GAMES_CSV_PATH}...')

    if not os.path.exists(config.GAMES_CSV_PATH):
        return None

    df = pd.read_csv(config.GAMES_CSV_PATH)
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

    expected_seasons = set(range(config.START_SEASON, max_season + 1))

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

        else:
            reg_season_df = df[(df['season'] == season) & (df['type'] == 'reg')]
            weeks = reg_season_df['week'].unique()
            target_weeks = set(range(1, 18))
            missing_weeks = set(weeks).difference(target_weeks)
            if len(missing_weeks > 0):
                raise DataIntegrityError(f"{season} reg season is missing weeks {missing_weeks}!")
            

def get_latest_season_and_type(df):
    """Gets the latest season and season type in the games data
    
    :param df: games data
    :type df: pandas.DataFrame
    :return: tuple of (latest_season, latest_season_type)
    :rtype: tuple
    """
    if df is None:
        return (None, None)

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    df = df[df['state_of_game'] == 'POST']
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
            if config.SEASON_TYPES_ORDER[season_type] > config.SEASON_TYPES_ORDER[latest_season_type]:
                latest_season_type = season_type

    return latest_season_type


def truncate(df, latest_season, latest_season_type):
    """Removes the latest season and season type from df.
    
    :param df: dataframe of games data
    :type df: pandas.DataFrame
    :param latest_season: last season of data
    :type latest_season: int
    :param latest_season_type: type of the latest season
    :type latest_season_type: str
    :return: truncated dataframe
    :rtype: pandas.DataFrame
    """
    return df[(df['season'] != latest_season) & (df['type'] != latest_season_type)]


def get_next_season_and_type(season, season_type, order='next'):
    """The next or previous season and type
    
    :param season: year of season
    :type season: int
    :param season_type: type of season (pre, reg, post)
    :type season_type: str
    :return: tuple of (season, season_type)
    :rtype: tuple
    """
    if season is None and season_type is None:
        return (config.START_SEASON, config.SEASON_TYPES[0])

    if order not in ('next', 'prev'):
        raise ValueError(f"given order {order} not in accepted types (next, prev).")

    if not isinstance(season, (np.int64, int)):
        raise ValueError(f"Season is type {type(season)}, it should be type 'int'.")
        
    if season < config.START_SEASON or season > config.CURRENT_SEASON:
        raise ValueError(f"Invalid season: {season}, must be in >= {config.START_SEASON} and <= {config.CURRENT_SEASON} ")

    if season_type not in config.SEASON_TYPES:
        raise ValueError(f"Start season type {season_type} not valid.")
    
    if (season, season_type) == (config.CURRENT_SEASON, 'post'):
        return None
    
    if (season, season_type) == (config.START_SEASON, 'pre'):
        return (config.START_SEASON, 'reg')

    grid = get_seasons_grid(config.START_SEASON, config.CURRENT_SEASON)

    for index, (season_and_type) in enumerate(grid):
        if (season, season_type) == season_and_type:
            if order == 'next':
                return grid[index + 1]
            else:
                return grid[index - 1]


def get_seasons_grid(start_season, start_season_type):
    """Enumerates all combos of season and season types
    
    :param start_season: year of season to start the grid
    :type start_season: int
    :param start_season_type: type of season to start the grid (pre, reg, post)
    :type start_season_type: str
    :return: list of (season, season type) tuples
    :rtype: list of tuples
    """
    if start_season not in list(range(config.START_SEASON, config.CURRENT_SEASON+1)):
        raise ValueError(f"Start season of {start_season} not valid.")
    
    if start_season_type not in config.SEASON_TYPES:
        raise ValueError(f"Start season type {start_season_type} not valid.")
    
    initial_season_types = [s for s in config.SEASON_TYPES if config.SEASON_TYPES_ORDER[s] >= config.SEASON_TYPES_ORDER[start_season_type] ]
    grid = [(start_season, season_type) for season_type in initial_season_types]

    if start_season < config.CURRENT_SEASON:
        for season in range(start_season + 1, config.CURRENT_SEASON + 1):
            grid += [(season, season_type) for season_type in config.SEASON_TYPES]

    return grid


def extract_game_data(season, season_type):
    """Runs the nflscrapr docker container for the given season and type
    
    :param season: year of season
    :type season: int
    :param season_type: type of season (pre, reg, post)
    :type season_type: str
    :return: the output of the call to nflscrapr as a dataframe
    :rtype: pandas.DataFrame
    """
    docker_command = f"games --year={season} --type={season_type}" 
    run_docker_container(
        config.DOCKER_CONTAINER,
        docker_command,
        **config.DOCKER_CONTAINER_ARGS
    )
    return extract_dumped_data()


def run_docker_container(container, command=None, **kwargs):
    """Runs the given docker container
    
    :param container: name of docker container
    :type container: str
    :param command: command to run in docker conatainer, defaults to None
    :type command: str, optional
    """
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


def extract_dumped_data():
    """Loads the data that was dumped from the docker container run
    
    :return: pandas dataframe
    :rtype: pandas.DataFrame
    """
    if not os.path.exists(config.DUMP_CSV_PATH):
        raise ValueError(f"Uh oh! {config.DUMP_CSV_PATH} does not exist!")

    return pd.read_csv(config.DUMP_CSV_PATH)


def load_to_csv(df):
    """Loads the dataframe into a csv.
    
    :param df: dataframe of games data
    :type df: pandas.DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    if not os.path.exists(config.GAMES_CSV_PATH):
        df.to_csv(config.GAMES_CSV_PATH, index=False) 
    else:
        current_df = extract_current_data()
        updated_df = pd.concat([current_df, df])
        updated_df.drop_duplicates(inplace=True)
        updated_df.to_csv(config.GAMES_CSV_PATH, index=False)


def run():
    """
    Runs the workflow for extracting and loading games data.
    - Finds the starting point for extracting new data
    - Extracts new data using runs of nflscrapr docker container
    - Saves data into csv
    """
    games_data = extract_current_data()
    data_integrity_check(games_data)
    
    latest_season, latest_season_type = get_latest_season_and_type(games_data) 

    logging.info(f"Latest season and type in current data: {(latest_season, latest_season_type)}")

    if latest_season is None:
        batch_start_season, batch_start_type = config.START_SEASON, config.SEASON_TYPES[0]

    else:
        games_data = truncate(games_data, latest_season, latest_season_type)
        batch_start_season, batch_start_type = latest_season, latest_season_type
    
    logging.info(f"Starting batch at {(batch_start_season, batch_start_type)}...")
    
    batches = get_seasons_grid(batch_start_season, batch_start_type)

    for batch in batches:
        season, season_type = batch 
        logging.info(f"Extracting data for {season}-{season_type}...")
        data = extract_game_data(season, season_type)
        load_to_csv(data)