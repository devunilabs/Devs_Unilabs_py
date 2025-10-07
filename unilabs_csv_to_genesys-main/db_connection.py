from sqlalchemy import create_engine


def get_engine(conn_details: dict):
    conn_str = f'mssql+pyodbc://{conn_details['user']}:{conn_details['pass']}@{conn_details['dsn']}'
    return create_engine(conn_str)
