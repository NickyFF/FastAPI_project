from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.getenv("PASSWORD")
DATABASE_URL = 'postgresql://postgres:' + PASSWORD + '@localhost:5432/dbname'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)
Base = declarative_base()