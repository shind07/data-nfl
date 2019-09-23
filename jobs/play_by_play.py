import os
import logging

import pandas as pd 

logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


DATA_URL = 'https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/{season_type}_season/{season_abbrev}_pbp_{season}.csv'
SEASON_TYPES = ['pre', 'regular', 'post']
CSV_PREFIXES= ['pre', 'reg', 'post']
DATA_START_YEAR, DATA_END_YEAR = (2009, 2018)

# move to env variables
DATA_DIR = './data'
PLAY_BY_PLAY_CSV='play_by_play.csv'


class FileNotFoundException(Exception):
    pass


def fetch_latest_season(data='play_by_play'):
    # try:
    #     data = pd.read_csv(os.path.join(DATA_DIR, PLAY_BY_PLAY_CSV))
    # except FileNotFoundException:
    #     return
    return None 


def extract(season):
    logging.info(f'extracting data for {season} season...')
    full_data = None

    for season_type, prefix in zip(SEASON_TYPES, CSV_PREFIXES):

        target_url = DATA_URL.format(
            season_type=season_type,
            season_abbrev=prefix,
            season=season
        )

        print(target_url)
        data = pd.read_csv(target_url, low_memory=False)

        data['Season'] = season 
        data['Season_Type'] = season_type

        if full_data is None:
            full_data = data 
        else:
            full_data = pd.concat([full_data, data])
    
    return full_data

def load(data):
    logging.info('loading data....')
    data.to_csv(os.path.join(DATA_DIR, PLAY_BY_PLAY_CSV))


def main():
    most_recent_season = fetch_latest_season()

    if most_recent_season is None:
        most_recent_season = DATA_START_YEAR
    
    elif most_recent_season == DATA_END_YEAR:
        return

    seasons_to_extract = range(most_recent_season)
    data = extract(2018)
    load(data)


if __name__ == '__main__':
    main()