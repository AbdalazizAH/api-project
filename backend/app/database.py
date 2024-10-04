# backend/app/database.py
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SettingsSupabase:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")


settings_supabase = SettingsSupabase()


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.init_db()
        return cls._instance

    def init_db(self):
        SQLALCHEMY_DATABASE_URL = f"postgresql://{settings_supabase.POSTGRES_USER}:{settings_supabase.POSTGRES_PASSWORD}@{settings_supabase.POSTGRES_HOST}:{settings_supabase.POSTGRES_PORT}/{settings_supabase.POSTGRES_DATABASE}"
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.Base = declarative_base()

    def create_tables_if_not_exist(self):
        inspector = inspect(self.engine)

        for table in self.Base.metadata.tables.values():
            if not inspector.has_table(table.name):
                table.create(self.engine)
                print(f"Table '{table.name}' created.")
            else:
                print(f"Table '{table.name}' already exists.")

    def get_db(self):
        self.create_tables_if_not_exist()
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Create a single instance of the Database class
db = Database()

# Use these in your models and other parts of your application
engine = db.engine
Base = db.Base
get_db = db.get_db
