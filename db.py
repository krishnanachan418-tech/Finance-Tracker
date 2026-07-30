import os
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    """Create and return a new MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "finance_tracker"),
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        raise
