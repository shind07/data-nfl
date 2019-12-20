import logging

import db
from . import (
    config,
    etl_tools,
    nflscrapr
)

TEST_GAME_IDS = (2017090700, 2017091007, 2017091008)


def _extract_games_game_ids(db_conn):
    query = "SELECT game_id FROM games WHERE state_of_game = 'POST'"
    return etl_tools.extract_from_db(db_conn, query)


def _extract_play_by_play_game_ids(db_conn):
    query = "SELECT DISTINCT game_id FROM play_by_play"
    return etl_tools.extract_from_db(db_conn, query)


def _extract_play_by_play(game_id):
    """Runs the nflscrapr play by play R script for the game_id

    :param game_id: id of the game
    :type game_id: int
    :return: the output of the call to nflscrapr as a dataframe
    :rtype: pandas.DataFrame
    """
    nflscrapr.run(
        'play_by_play',
        game_id=game_id,
    )
    nflscrapr_output = etl_tools.extract_from_csv(config.PLAY_BY_PLAY_DUMP_CSV_PATH)
    return nflscrapr_output


def run():
    db_conn = db.get_db_eng()

    all_played_game_ids = _extract_games_game_ids(db_conn)
    existing_game_ids = _extract_play_by_play_game_ids(db_conn)
    missing_game_ids = set(all_played_game_ids['game_id']) - set(existing_game_ids['game_id'])

    logging.info(f"Grabbing play by play data for {len(missing_game_ids)} games...")

    backfill_limit = 10
    for i, game_id in enumerate(missing_game_ids, start=1):
        if i > backfill_limit: break
        logging.info(f"{i}/{backfill_limit}: Extracting play by play data for game_id={game_id}...")
        play_by_play_data = _extract_play_by_play(game_id)
        logging.info(f"Data extracted. Loading {len(play_by_play_data)} rows...")
        etl_tools.load_to_db(
            db_conn,
            'play_by_play',
            play_by_play_data,
        )
