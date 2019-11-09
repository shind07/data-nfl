import logging
import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from jobs import games, config

logger = logging.getLogger('test_logger')
logger.setLevel(logging.DEBUG)

class TestGames(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the test csv"""
        cls.test_games_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_data/test_games.csv'
        )
        cls.test_df = pd.read_csv(cls.test_games_path)
    
    def test_data_integrity_check(self):
        """
        4 conditions must be met:
        - there must not be any gaps in the seasons
        - seasons must have all 3 season types (except most recent season)
        - seasons must have semantic ordering of season types (pre -> reg -> post)
        - data must have weeks 1-17 if type is reg
        """
        with self.assertRaises(ValueError) as cm:
            games.data_integrity_check("not a dataframe")
        logger.debug(cm.exception)

        good_dfs = [
            self.test_df[(self.test_df['season'] == 2011) & (self.test_df['type'] != 'post')],
            self.test_df[(self.test_df['season'] == 2011) & (self.test_df['type'] == 'pre')]
        ]

        for good_df in good_dfs:
            exception_raised = False
            try:
                games.data_integrity_check(good_df)
            except Exception as e:
                logging.debug(e)
                exception_raised = True
            self.assertFalse(exception_raised)

        bad_dfs = [
            self.test_df[(self.test_df['season'] == 2011) & (self.test_df['type'] != 'pre')],
            self.test_df[(self.test_df['season'] == 2011) & (self.test_df['type'] != 'reg')],
            self.test_df[(self.test_df['season'] != 2011) | (self.test_df['type'].isin(['reg', 'post']))],
            self.test_df[(self.test_df['season'] == 2011) & (~self.test_df['type'].isin(['reg', 'pre']))],
            self.test_df[self.test_df['season'] != 2012],
            self.test_df[(self.test_df['season'] == 2011) & (self.test_df['type'].isin(['reg', 'pre'])) & (self.test_df['week'] != 2)]
        ]

        for bad_df in bad_dfs:
            with self.assertRaises(games.DataIntegrityError) as cm:
                games.data_integrity_check(bad_df)
            logger.debug(cm.exception)
            
    def test_get_latest_season_type(self):
        """Test that the function preserves semantic ordering"""
        with self.assertRaises(ValueError) as cm:
            games.get_latest_season_type("not a list/tuple")
        logger.debug(cm.exception)

        ordered_season_types = ('pre', 'reg', 'post')
        for i in range(len(ordered_season_types)):
            latest_season_type = games.get_latest_season_type(ordered_season_types[:i+1])
            self.assertEqual(latest_season_type, ordered_season_types[i])

    def test_get_latest_season_and_type(self):
        """Test that function gets proper season and season type"""
        latest_season, latest_season_type = games.get_latest_season_and_type(self.test_df)
        self.assertEqual(latest_season, self.test_df['season'].max())

        latest_seasons_types = self.test_df[self.test_df['season'] == latest_season]["type"].unique()
        expected_latest_season_type = games.get_latest_season_type(list(latest_seasons_types))
        self.assertEqual(latest_season_type, expected_latest_season_type)

    def test_get_next_season_and_type(self):
        """Test that function can order season types semantically"""
        results = []
        for season_type in config.SEASON_TYPES:
            results.append(games.get_next_season_and_type(2011, season_type))
        
        self.assertEqual(results[0], (2011, 'reg'))
        self.assertEqual(results[1], (2011, 'post'))
        self.assertEqual(results[2], (2012, 'pre'))

        next_season_and_type = games.get_next_season_and_type(config.CURRENT_SEASON, 'post')
        self.assertIsNone(next_season_and_type)

        next_season_and_type = games.get_next_season_and_type(config.START_SEASON, 'pre', order='prev')
        self.assertIsNone(next_season_and_type)

        next_season_and_type = games.get_next_season_and_type(config.CURRENT_SEASON, 'post', order='prev')
        self.assertEqual(next_season_and_type, (config.CURRENT_SEASON, 'reg'))

        next_season_and_type = games.get_next_season_and_type(config.CURRENT_SEASON, 'pre', order='prev')
        self.assertEqual(next_season_and_type, (config.CURRENT_SEASON - 1, 'post'))

    def test_get_seasons_grid(self):
        """Test that the grid is properly populated"""
        with self.assertRaises(ValueError) as cm:
            grid = games.get_seasons_grid(2003, 'pre')
        logger.debug(cm.exception)

        with self.assertRaises(ValueError) as cm:
            grid = games.get_seasons_grid('2013', 'pre')
        logger.debug(cm.exception)

        with self.assertRaises(ValueError) as cm:
            grid = games.get_seasons_grid(2013, 'blah')
        logger.debug(cm.exception)

        grid = games.get_seasons_grid(2013, 'pre')
        first_season, first_season_type = grid[0]
        self.assertEqual(first_season, 2013)
        self.assertEqual(first_season_type, 'pre')

        latest_season, latest_season_type = grid[-1]
        self.assertEqual(latest_season, config.CURRENT_SEASON)
        self.assertEqual(latest_season_type, 'post')

        grid = games.get_seasons_grid(2013, 'pre')
        first_season, first_season_type = grid[0]
        self.assertEqual(first_season, 2013)
        self.assertEqual(first_season_type, 'pre')

        grid = games.get_seasons_grid(2013, 'reg')
        first_season, first_season_type = grid[0]
        self.assertEqual(first_season, 2013)
        self.assertEqual(first_season_type, 'reg')

        grid = games.get_seasons_grid(2013, 'post')
        first_season, first_season_type = grid[0]
        self.assertEqual(first_season, 2013)
        self.assertEqual(first_season_type, 'post')

        grid = games.get_seasons_grid(config.START_SEASON, 'pre')
        seasons = set([season_and_type[0] for season_and_type in grid])
        expected_number_of_seasons = len(list(range(config.START_SEASON, config.CURRENT_SEASON + 1)))
        self.assertEqual(min(seasons), config.START_SEASON)
        self.assertEqual(max(seasons), config.CURRENT_SEASON)
        self.assertEqual(len(seasons), expected_number_of_seasons)
        self.assertEqual(len(grid), expected_number_of_seasons*len(config.SEASON_TYPES))

    def test_truncate(self):
        
        df = self.test_df[self.test_df['season'].isin([2011, 2012, 2013])]
        latest_season_and_type = games.get_latest_season_and_type(df)
        self.assertEqual(latest_season_and_type, (2013, 'post'))
        games.data_integrity_check(df)

        df = games.truncate(df, *latest_season_and_type)
        latest_season_and_type = games.get_latest_season_and_type(df)
        self.assertEqual(latest_season_and_type, (2013, 'reg'))
        games.data_integrity_check(df)

        df = games.truncate(df, *latest_season_and_type)
        latest_season_and_type = games.get_latest_season_and_type(df)
        self.assertEqual(latest_season_and_type, (2013, 'pre'))
        games.data_integrity_check(df)

        df = games.truncate(df, *latest_season_and_type)
        latest_season_and_type = games.get_latest_season_and_type(df)
        self.assertEqual(latest_season_and_type, (2012, 'post'))
        games.data_integrity_check(df)
        

if __name__ == '__main__':
    unittest.main()