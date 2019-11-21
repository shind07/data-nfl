import sqlalchemy as db

PG_USERNAME = 'postgres'
PG_PASSWORD = 'password'
PG_HOST = 'postgres'
DB_NAME = 'nfl'


def connect_to_db():
    """Connect to a db with the given connection string

    Example usage:
        conn_str = db.get_connection_string()
        conn = db.connect_to_db(conn_str)
        results = conn.execute('select * from database')

    :param connection_string: [description]
    :type connection_string: [type]
    :return: [description]
    :rtype: [type]
    """
    connection_string = _get_connection_string()
    return db.create_engine(connection_string)


def _get_connection_string():
    return f"postgresql://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/{DB_NAME}"

