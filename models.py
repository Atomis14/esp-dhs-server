from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
  pass


class Message(Base):
  __tablename__ = 'messages'
  message_id:     Mapped[int]             = mapped_column(primary_key=True)
  created_at:     Mapped[datetime]        = mapped_column(server_default=func.now())
  topic:          Mapped[str]
  status:         Mapped[Optional[int]]
  type:           Mapped[str]
  configuration:  Mapped["Configuration"] = relationship(back_populates="message")

  def __repr__(self) -> str:
    return f"•Message(id: {self.message_id}, created_at: {self.created_at}, type: {self.type})"
  

class Configuration(Base):
  __tablename__ = 'configurations'
  configuration_id: Mapped[int]       = mapped_column(primary_key=True)
  message_id:       Mapped[int]       = mapped_column(ForeignKey("messages.message_id"), unique=True)
  message:          Mapped["Message"] = relationship(back_populates="configuration", single_parent=True)
  configuration:    Mapped[str]

  def __repr__(self) -> str:
    return f"•Configuration(id: {self.configuration_id}, message: {self.message}, configuration: {self.configuration})"