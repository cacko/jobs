from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import Optional


class DbConfig(BaseModel):
    url: str


class FirebaseConfig(BaseModel):
    admin_json: str


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


class Settings(BaseSettings):
    db: DbConfig
    api: ApiConfig
    aws: AWSConfig
    firebase: FirebaseConfig

    class Config:
        env_nested_delimiter = '__'


app_config = Settings()  # type: ignore
