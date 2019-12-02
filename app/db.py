import sqlalchemy as sa

import config


def connect_to_db():
    """Connect to a db with the given connection string

    Example usage:
        conn_str = db.get_connection_string()
        conn = db.connect_to_db(conn_str)
        results = conn.execute('select col1, col2 from database')

    :param connection_string: database connection string
    :type connection_string: str
    :return: sqlalchemy database engine
    :rtype: sqlalchemy.engine.base.Engine | sqlalchemy.engine.base.Connection
    """
    connection_string = _get_connection_string()
    return sa.create_engine(connection_string)


def _get_connection_string():
    """Formats a connection string using the configuration variables."""
    username = config.PG_USERNAME
    password = config.PG_PASSWORD
    host = config.PG_HOST
    db = config.DB_NAME
    return f"postgresql://{username}:{password}@{host}/{db}"
