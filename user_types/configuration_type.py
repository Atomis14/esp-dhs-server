from typing import TypedDict

class Configuration(TypedDict):
  base_mac_address: str
  efuse_default_mac: str
  efuse_custom_mac: str
  esp_idf_version: str
  chip_cores: int
  chip_features: int
  chip_model: int
  chip_revision: int
  flash_encryption_enabled: bool
  flash_encryption_mode: int
  secure_boot_enabled: bool
  aggressive_key_revoke_enabled: bool
  download_mode_disabled: bool
  security_download_enabled: bool
  anti_rollback_secure_version: int