import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Message, Configuration

load_dotenv()

engine = create_engine('sqlite://' + os.getenv('DB_PATH'))  # add echo=True parameter for logging
Base.metadata.create_all(engine)  # create the tables
    

def add_row(rows):
  with Session(engine) as session:
    if type(rows) in [list, tuple]: # multiple rows
      session.add_all(rows)
    elif isinstance(rows, object):  # single row
      session.add(rows)
    else:
      raise Exception('Parameter type not valid.')
    session.commit()