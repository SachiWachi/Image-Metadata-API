# database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load the environment variables from the .env file
load_dotenv()

# Fetch the URL securely. 
# We use os.getenv() so it doesn't crash if the variable is missing, 
# but we raise an explicit error to help with debugging.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No DATABASE_URL found. Please check your .env file.")

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()