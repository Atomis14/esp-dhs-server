from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Message, Configuration

def _setup_database():

  engine = create_engine('sqlite:///database.sqlite3', echo=True)

  Base.metadata.create_all(engine)  # create the tables

  with Session(engine) as session:
    example_message = Message(type="ddd")
    example_configuration = Configuration(message=example_message)
    session.add(example_message)
    session.add(example_configuration)
    session.commit()
    print(example_message)
    print(example_configuration)
    


def _add_row():
  pass


_setup_database()

