from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
  pass


class Message(Base):  # MQTT messages
  __tablename__ = 'messages'
  message_id:     Mapped[int]             = mapped_column(primary_key=True)
  created_at:     Mapped[datetime]
  topic:          Mapped[str]             # MQTT topic
  status:         Mapped[Optional[int]]   # return code, only when sent
  type:           Mapped[str]             # sent or received
  configuration:  Mapped['Configuration'] = relationship(back_populates='message')  # received configuration, if any

  def __repr__(self) -> str:
    return f'•Message(id: {self.message_id}, created_at: {self.created_at}, topic: {self.topic}, status: {self.status}, type: {self.type})'
  

class Configuration(Base):  # configurations that were returned from the ESP32
  __tablename__ = 'configurations'
  configuration_id:               Mapped[int]       = mapped_column(primary_key=True)
  message_id:                     Mapped[int]       = mapped_column(ForeignKey('messages.message_id'), unique=True)
  message:                        Mapped['Message'] = relationship(back_populates='configuration', single_parent=True)
  # ESP32-S3 security configuration fields
  base_mac_address:               Mapped[str]
  efuse_default_mac:              Mapped[str]
  efuse_custom_mac:               Mapped[str]
  esp_idf_version:                Mapped[str]
  chip_cores:                     Mapped[int]
  chip_features:                  Mapped[int]
  chip_model:                     Mapped[int]
  chip_revision:                  Mapped[int]
  flash_encryption_enabled:       Mapped[bool]
  flash_encryption_mode:          Mapped[int]
  secure_boot_enabled:            Mapped[bool]
  aggressive_key_revoke_enabled:  Mapped[bool]
  download_mode_disabled:         Mapped[bool]
  memory_protection_enabled:      Mapped[bool]
  memory_protection_locked:       Mapped[bool]
  security_download_enabled:      Mapped[bool]
  anti_rollback_secure_version:   Mapped[int]
  atecc_connected:                Mapped[bool]


  def __repr__(self) -> str:
    return f'•Configuration(id: {self.configuration_id}, message: {self.message}, configuration: {self.configuration})'
  

class Flash(Base):  # flash beginnings and ends
  __tablename__ = 'flashes'
  flash_id:         Mapped[int]                 = mapped_column(primary_key=True)
  start:            Mapped[datetime]            # datetime when flash was started
  end:              Mapped[Optional[datetime]]  # datetime when flash was finished
  status:           Mapped[str]   # 'pending', 'error', 'success'
  # security features as in security_features_type.py (if true, the feature should have been activated in this flash)
  flashencryption:  Mapped[bool]                = mapped_column(default=False)
  secureboot:       Mapped[bool]                = mapped_column(default=False)
  memoryprotection: Mapped[bool]                = mapped_column(default=False)

  def __repr__(self) -> str:
    return f'•Flash(id: {self.flash_id}, start: {self.start}, end: {self.end}, status: {self.status})'