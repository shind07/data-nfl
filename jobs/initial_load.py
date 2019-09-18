import os
import logging

import pandas as pd 

DATA_URL = 'https://github.com/ryurko/nflscrapR-data/blob/master/play_by_play_data/{season_type}/{prefix}_{year}.csv'
SEASON_TYPES = ['pre_season', 'regular_season', 'post_season']
CSV_PREFIXESb= ['pre_pbp', 'reg_pbp','post_pbp']
DATA_START_YEAR, DATA_END_YEAR = (2009, 2018)

# move to env variables
DATA_DIR = 'data'
PLAY_BY_PLAY_CSV='play_by_play.csv'

def fetch_latest_season(data='play_by_play'):
    pass

def extract(season):
    pass

def main():
    most_recent_season = fetch_latest_season()

    if most_recent_season is None:
        most_recent_season = DATA_START_YEAR
    
    if most_recent_season == DATA_END_YEAR:
        return

    seasons_to_extract = range(most_recent_season)
    data = extract()

if __name__ == '__main__':
    main()