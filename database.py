from sqlalchemy import ForeignKey, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from datetime import datetime

def _setup_database():
  class Base(DeclarativeBase):
    pass

  class Message(Base):
    __tablename__ = 'messages'
    message_id:     Mapped[int]             = mapped_column(primary_key=True)
    created_at:     Mapped[datetime]        = mapped_column(server_default=func.now())
    type:           Mapped[str]
    configuration:  Mapped["Configuration"] = relationship(back_populates="message")

    def __repr__(self) -> str:
      return f"• Message(id: {self.message_id}, created_at: {self.created_at}, type: {self.type})"

  class Configuration(Base):
    __tablename__ = 'configurations'
    configuration_id: Mapped[int]       = mapped_column(primary_key=True)
    message_id:       Mapped[int]       = mapped_column(ForeignKey("messages.message_id"), unique=True)
    message:          Mapped["Message"] = relationship(back_populates="configuration", single_parent=True)

    def __repr__(self) -> str:
      return f"• Configuration(id: {self.configuration_id}, message: {self.message})"

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

