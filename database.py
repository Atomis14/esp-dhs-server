import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Message, Configuration

load_dotenv()

engine = create_engine('sqlite://' + os.getenv('DB_PATH'))  # add echo=True parameter for logging
Base.metadata.create_all(engine)  # create the tables
    

def add_row(object):
  with Session(engine) as session:
    session.add(object)
    session.commit()