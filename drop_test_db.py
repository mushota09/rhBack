"""
Script to drop the test database by terminating all connections first
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Connection parameters
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Connect to the main database (not the test database)
conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

try:
    print(f"Connecting to {DB_NAME}...")
    with psycopg.connect(conn_string, autocommit=True) as conn:
        with conn.cursor() as cur:
            # Terminate all connections to test_rh_db
            print("Terminating all connections to test_rh_db...")
            cur.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = 'test_rh_db'
                AND pid <> pg_backend_pid();
            """)
            result = cur.fetchall()
            print(f"Terminated {len(result)} connections")

            # Drop the test database
            print("Dropping test_rh_db...")
            cur.execute("DROP DATABASE IF EXISTS test_rh_db;")
            print("✅ test_rh_db dropped successfully!")

except Exception as e:
    print(f"❌ Error: {e}")

