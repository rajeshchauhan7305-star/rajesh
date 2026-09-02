import os
from contextlib import closing

import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'edusubmit'),
    'autocommit': True,
    'charset': 'utf8mb4',
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def db_fetch_all(query, params=()):
    with closing(get_connection()) as connection:
        with closing(connection.cursor(dictionary=True)) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def db_fetch_one(query, params=()):
    with closing(get_connection()) as connection:
        with closing(connection.cursor(dictionary=True)) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()


def db_execute(query, params=()):
    with closing(get_connection()) as connection:
        with closing(connection.cursor(dictionary=True)) as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
