
import sys
import mysql.connector
from mysql.connector import Error

# MySQL connection settings
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "hospital_db"


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print("=" * 55)
        print(" DATABASE CONNECTION FAILED")
        print("=" * 55)
        print(f"Error: {e}")
        print("\nCheck that:")
        print("  1. MySQL server is running")
        print("  2. Database 'hospital_db' exists (run schema.sql first)")
        print("  3. DB_USER / DB_PASSWORD in database.py are correct")
        sys.exit(1)
