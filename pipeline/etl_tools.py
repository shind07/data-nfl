"""
A collection of functions to help with standard ETL operations, with
both csv's and databases.

TODO:
- make the load_to_db(if_exist='replace') functionality an atomic rewrite,
  rather than a drop and create style.
"""
import logging
import os

import pandas as pd
import sqlalchemy


def extract_from_csv(csv_path):
    """Loads csv into dataframe.

    :param csv_path: path to csv to load
    :type csv_path: str
    :return: dataframe if file exists, else None
    :rtype: pandas.DataFrame
    """
    if not os.path.exists(csv_path):
        raise ValueError(f"Path {csv_path} doesn't exist!")

    if not csv_path.endswith(".csv"):
        raise ValueError(f"File {csv_path} is not a .csv file!")

    logging.info(f'Loading games data from {csv_path}...')
    return pd.read_csv(csv_path)


def extract_from_db(db_conn, query):
    """Extracts data from a database

    :param db_conn: sqlalchemy database connection
    :type db_conn: sqlalchemy.engine.base.Engine | sqlalchemy.engine.base.Connection
    :param query: query to run on database to extract data
    :type query: str
    """
    _check_db_conn(db_conn)
    return pd.read_sql(query, db_conn)


def load_to_csv(df, csv_path, append=False, sort_by=None, sort_order='asc'):
    """Loads dataframe to a csv.

    :param df: dataframe to load to a csv
    :type df: pandas.DataFrame
    :param csv_path: path to csv
    :type csv_path: str
    :param append: append to existing data, defaults to False
    :type append: bool, optional
    :param sort_by: column to sort by, defaults to None
    :type sort_by: str, optional
    :param sort_order: sort ascending or descending, defaults to 'asc'
    :type sort_order: str, optional
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Type of df is {type(df)}, it should be pandas.DataFrame")

    if not csv_path.endswith(".csv"):
        raise ValueError(f"File {csv_path} is not a .csv file!")

    if append:
        if not os.path.exists(csv_path):
            raise ValueError(f"File {csv_path} doesn't exist, cannot append!")
        existing_data = extract_from_csv(csv_path)
        df = pd.concat([existing_data, df])

    if sort_by:
        if sort_order not in ('asc', 'desc'):
            raise ValueError(f"Sort order {sort_order} not one of 'asc', 'desc'")
        ascending = True if sort_order == 'asc' else False
        df = df.sort_values(by=sort_by, ascending=ascending)

    df.to_csv(csv_path, index=False)


def load_to_db(db_conn, table_name, df, if_exists="append"):
    """Writes the data in df to table_name.

    Currently, the replace function is NOT atomic. Added to TODO.

    :param db_conn: sqlalchemy database connection
    :type db_conn: sqlalchemy.engine.base.Engine | sqlalchemy.engine.base.Connection
    :param table_name: name of table to write to
    :type table_name: str
    :param df: dataframe containing data to write to db
    :type df: pandas.DataFrame
    """
    if if_exists not in ("fail", "replace", "append"):
        raise ValueError(f"{if_exists} not an accepted value for if_exists. Must be (fail|replace|append)")
    _check_db_conn(db_conn)

    # manually overwrite this so pandas doesn't dynamically recreate the schema
    if if_exists == "replace":
        db_conn.execute(f"TRUNCATE TABLE {table_name};")
        if_exists = "append"

    df.to_sql(table_name, db_conn, if_exists=if_exists, index=False)


def _check_db_conn(db_conn):
    """Make sure the db_conn is the correct type.

    :param db_conn: sqlalchemy database connection
    :type db_conn: sqlalchemy.engine.base.Engine | sqlalchemy.engine.base.Connection
    """
    if not isinstance(db_conn, (sqlalchemy.engine.base.Engine, sqlalchemy.engine.base.Connection)):
        raise TypeError(f"Given database connection is not type sqlalchemy.engine.base.(Engine | Connection).")
