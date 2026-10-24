import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://de:de@localhost:5432/taxi")
DATA_DIR = os.getenv("DATA_DIR", "./data")
TLC_BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data"