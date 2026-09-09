from unittest.mock import patch

from config.database import db_fetch_one


def test_database_falls_back_to_sqlite_when_mysql_is_unavailable():
    with patch('config.database.mysql.connector.connect', side_effect=Exception('MySQL unavailable')):
        row = db_fetch_one('SELECT email FROM users WHERE email = %s', ('admin@example.com',))
        assert row is not None
        assert row['email'] == 'admin@example.com'
