from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
from appdirs import user_config_dir
from jobs import __name__
from os import environ
import yaml

USER_CONFIG_PATH = Path(user_config_dir(appname=__name__))
DEFAULT_CONFIG_FILE_PATH = USER_CONFIG_PATH / "settings.yaml"

config_file = Path(environ.get("JOBS_CONFIG_FILE", DEFAULT_CONFIG_FILE_PATH.as_posix()))

try:
    assert config_file.parent.exists()
except AssertionError:
    config_file.parent.mkdir(parents=True)


try:
    assert config_file.exists()
except AssertionError:
    raise RuntimeError(f"No config file as {config_file}")


class DbConfig(BaseModel):
    url: str


class FirebaseConfig(BaseModel):
    admin_json: str
    db_url: str


class ApiConfig(BaseModel):
    host: str
    port: int
    assets: str
    workers: Optional[int] = Field(default=1)
    web_host: Optional[str] = Field(default="https://jobs.cacko.net")


class AWSConfig(BaseModel):
    cloudfront_host: str
    access_key_id: str
    secret_access_key: str
    s3_region: str
    storage_bucket_name: str
    media_location: str


class MashaConfig(BaseModel):
    host: str
    port: int
    
class AccessConfig(BaseModel):
    admin: list[str]


class Settings(BaseModel):
    db: DbConfig
    api: ApiConfig
    aws: AWSConfig
    firebase: FirebaseConfig
    masha: MashaConfig
    access: AccessConfig


data = yaml.full_load(config_file.read_text())


app_config = Settings(**data)
