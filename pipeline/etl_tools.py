import logging
import os

import pandas as pd


def extract_from_csv(csv_path):
    """Loads csv into dataframe.

    :param csv_path: path to csv to load
    :type csv_path: st
    :return: dataframe if file exists, else None
    :rtype: pandas.DataFrame
    """
    if not os.path.exists(csv_path):
        raise ValueError(f"Path {csv_path} doesn't exist!")

    if not csv_path.endswith(".csv"):
        raise ValueError(f"File {csv_path} is not a .csv file!")

    logging.info(f'Loading games data from {csv_path}...')
    return pd.read_csv(csv_path)


def extract_from_db():
    pass


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
        if sort_by not in list(df.columns):
            raise ValueError(f"sort column {sort_by} doesnt exist in the df column names.")

        if sort_order not in ('asc', 'desc'):
            raise ValueError(f"Sort order {sort_order} not one of 'asc', 'desc'")

        ascending = True if sort_order == 'asc' else False
        df = df.sort_values(by=sort_by, ascending=ascending)

    df.to_csv(csv_path, index=False)


def load_to_db():
    pass
