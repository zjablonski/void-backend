import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

load_dotenv()


def wait_for_postgres(database_url):
    engine = create_engine(database_url)
    retries = 5
    while retries:
        try:
            # Attempt to connect to the database
            with engine.begin() as conn:
                # The connection is valid, no need to execute anything
                print("Connected to PostgreSQL, database is ready.")
                return
        except OperationalError:
            retries -= 1
            print(f"Waiting for PostgreSQL, {retries} retries left...")
            time.sleep(5)

if __name__ == "__main__":
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    wait_for_postgres(database_url)
