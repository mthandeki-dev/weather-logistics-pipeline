import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load the project's env file (named `config.env`) explicitly so values are available
# 1. Get the absolute path of the directory where load.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Point directly to the .env file in that exact directory
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)


# Build the connection string dynamically
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# The Database URL format for SQLAlchemy is:
# postgresql://username:password@host:port/database_name

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

#The path for the processed data file that will be loaded into PostgreSQL
PROCESSED_DATA_DIR = "./data/processed"

#the actual name of the input file for the cleaned CSV that will be loaded into PostgreSQL

INPUT_FILE = f"{PROCESSED_DATA_DIR}/clean_logistics_data.csv"


def load_data_to_postgres():
    # 1. Check if the processed data file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run transform.py first.")
        return

    # 2. Read the cleaned CSV back into a Pandas DataFrame
    print(f"Reading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # 3. Validate DB port and create the database engine connection
    if DB_PORT is None or str(DB_PORT).strip() == "":
        print("Warning: DB_PORT not set; defaulting to 5432")
        port = "5432"
    else:
        port = str(DB_PORT).strip()

    if not port.isdigit():
        raise ValueError(f"Invalid DB_PORT value: {DB_PORT!r}. Must be an integer.")

    # Rebuild DATABASE_URL with the validated port
    validated_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"

    try:
        engine = create_engine(validated_url)
    except Exception as exc:
        print(f"Failed to create database engine: {exc}")
        raise

    # 4. Load the data into PostgreSQL
    # 'if_exists="append"' means it will add new rows to the table each time the pipeline runs
    # 'index=False' prevents Pandas from creating an extra column for row numbers
    print("Loading data into PostgreSQL database...")
    try:
        df.to_sql(
            name="fact_weather_logistics",
            con=engine,
            if_exists="append",
            index=False,
        )
    except OperationalError as oe:
        print("Database operational error while writing data:", oe)
        print("Possible causes: wrong DB credentials, Postgres not running, or pg_hba.conf rejecting authentication.")
        print("Remediation options:")
        print(" - Verify `config.env` credentials match the Postgres instance.")
        print(" - If you intend to use the Docker Postgres, run: docker-compose up -d")
        print(" - To reset the `postgres` user's password on the host Postgres: ")
        print("     sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD 'your_password';\"")
        print(" - If Postgres uses different auth, update /etc/postgresql/*/main/pg_hba.conf accordingly and restart Postgres.")
        raise

    print(
        f"Success! Successfully loaded {len(df)} records into the 'fact_weather_logistics' table."
    )


if __name__ == "__main__":
    load_data_to_postgres()