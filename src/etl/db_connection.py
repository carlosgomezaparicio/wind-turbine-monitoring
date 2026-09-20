import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_url = URL.create(
    "mssql+pyodbc",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_SERVER,
    database=DB_NAME,
    query={"driver": "ODBC Driver 18 for SQL Server"},
)

engine = create_engine(connection_url)

if __name__ == "__main__":
    with engine.connect() as conn:
        print("Connected successfully.")