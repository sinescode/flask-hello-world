# extensions.py
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
Base = declarative_base()

# Use env variable for engine URI
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
