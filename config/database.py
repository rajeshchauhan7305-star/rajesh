import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

import bcrypt
import mysql.connector


ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', str(ROOT / 'edusubmit.db'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'edusubmit'),
    'autocommit': True,
    'charset': 'utf8mb4',
}


def _normalize_query(query: str) -> str:
    normalized = query.replace('NOW()', 'CURRENT_TIMESTAMP')
    return re.sub(r'%s', '?', normalized)


def _seed_sqlite_data(connection):
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student', 'teacher', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            due_date DATE NOT NULL,
            max_marks INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES users(user_id)
        )
        '''
    )
    connection.execute(
        '''
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            submission_date DATETIME NOT NULL,
            marks_obtained INTEGER DEFAULT NULL,
            teacher_feedback TEXT DEFAULT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY(assignment_id) REFERENCES assignments(assignment_id),
            FOREIGN KEY(student_id) REFERENCES users(user_id)
        )
        '''
    )

    users_count = connection.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if users_count == 0:
        default_users = [
            ('Admin One', 'admin@example.com', 'password123', 'admin'),
            ('Teacher One', 'teacher@example.com', 'password123', 'teacher'),
            ('Student One', 'student@example.com', 'password123', 'student'),
        ]
        for name, email, plain_password, role in default_users:
            password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            connection.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                (name, email, password_hash, role),
            )

    assignments_count = connection.execute('SELECT COUNT(*) FROM assignments').fetchone()[0]
    if assignments_count == 0:
        connection.execute(
            'INSERT INTO assignments (subject_name, title, description, due_date, max_marks, created_by) VALUES (?, ?, ?, ?, ?, ?)',
            ('Computer Science', 'DBMS Practical', 'Submit a practical assignment on SQL joins.', '2026-08-01', 50, 1),
        )
        connection.execute(
            'INSERT INTO assignments (subject_name, title, description, due_date, max_marks, created_by) VALUES (?, ?, ?, ?, ?, ?)',
            ('Mathematics', 'Calculus Worksheet', 'Solve the given calculus problems.', '2026-08-10', 40, 1),
        )

    connection.commit()


def get_sqlite_connection():
    connection = sqlite3.connect(SQLITE_DB_PATH)
    connection.row_factory = sqlite3.Row
    _seed_sqlite_data(connection)
    return connection


def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception:
        return get_sqlite_connection()


def db_fetch_all(query, params=()):
    query = _normalize_query(query)
    with closing(get_connection()) as connection:
        cursor = connection.cursor(dictionary=True) if hasattr(connection.cursor(), 'keys') else connection.cursor()
        if isinstance(connection, sqlite3.Connection):
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        if isinstance(connection, sqlite3.Connection):
            return [dict(row) for row in rows]
        return rows


def db_fetch_one(query, params=()):
    query = _normalize_query(query)
    with closing(get_connection()) as connection:
        cursor = connection.cursor(dictionary=True) if hasattr(connection.cursor(), 'keys') else connection.cursor()
        if isinstance(connection, sqlite3.Connection):
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if isinstance(connection, sqlite3.Connection):
            return dict(row) if row is not None else None
        return row


def db_execute(query, params=()):
    query = _normalize_query(query)
    with closing(get_connection()) as connection:
        cursor = connection.cursor(dictionary=True) if hasattr(connection.cursor(), 'keys') else connection.cursor()
        if isinstance(connection, sqlite3.Connection):
            cursor = connection.cursor()
        cursor.execute(query, params)
        if isinstance(connection, sqlite3.Connection):
            connection.commit()
            return cursor.lastrowid
        return cursor.lastrowid
