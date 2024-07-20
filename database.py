from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Message, Configuration


engine = create_engine('sqlite:///database.sqlite3')  # add echo=True parameter for logging
Base.metadata.create_all(engine)  # create the tables
    

def add_row(object):
  with Session(engine) as session:
    session.add(object)
    session.commit()