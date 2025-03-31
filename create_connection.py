# create_connection.py (fixed)
import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create and return a MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='admin@SQLpython',
            database='smart_kitchen'
        )
        return connection
    except Error as e:
        print(f"Connection error: {e}")
        return None