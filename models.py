from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
  pass


class Message(Base):  # MQTT messages
  __tablename__ = 'messages'
  message_id:     Mapped[int]             = mapped_column(primary_key=True)
  created_at:     Mapped[datetime]        = mapped_column(server_default=func.now())
  topic:          Mapped[str]             # MQTT topic
  status:         Mapped[Optional[int]]   # return code, only when sent
  type:           Mapped[str]             # sent or received
  configuration:  Mapped["Configuration"] = relationship(back_populates="message")  # received configuration, if any

  def __repr__(self) -> str:
    return f"•Message(id: {self.message_id}, created_at: {self.created_at}, topic: {self.topic}, status: {self.status}, type: {self.type})"
  

class Configuration(Base):  # configurations that were returned from the ESP32
  __tablename__ = 'configurations'
  configuration_id: Mapped[int]       = mapped_column(primary_key=True)
  message_id:       Mapped[int]       = mapped_column(ForeignKey("messages.message_id"), unique=True)
  message:          Mapped["Message"] = relationship(back_populates="configuration", single_parent=True)
  configuration:    Mapped[str]

  def __repr__(self) -> str:
    return f"•Configuration(id: {self.configuration_id}, message: {self.message}, configuration: {self.configuration})"
  

class Flash(Base):  # flash beginnings and ends
  __tablename__ = 'flashes'
  flash_id:   Mapped[int]                 = mapped_column(primary_key=True)
  start:      Mapped[datetime]            = mapped_column(server_default=func.now())  # datetime when flash was started
  end:        Mapped[Optional[datetime]]  = mapped_column(server_onupdate=func.now()) # datetime when flash was finished
  features:   Mapped[str]                 # security features that were activated

  def __repr__(self) -> str:
    return f"•Flash(id: {self.flash_id}, created_at: {self.created_at}, features: {self.features})"