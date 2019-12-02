
import pandas as pd


def main(db_conn, **kwargs):
    query = "SELECT * FROM games WHERE state_of_game = 'POST' ORDER BY game_id DESC"
    results = pd.read_sql(query, db_conn)
    return results.to_json(orient="records")
