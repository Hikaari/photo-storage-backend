
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml
from typing import Optional

class S3Settings(BaseSettings):
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
    endpoint_url: Optional[str] = None

class OIDCSettings(BaseSettings):
    client_id: str
    client_secret: str
    server_metadata_url: str

class JWTSettings(BaseSettings):
    secret_key: str = "supersecret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

class Settings(BaseSettings):
    database_url: str
    s3: S3Settings
    oidc: OIDCSettings
    jwt: JWTSettings = JWTSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter='__',
    )

def get_settings() -> Settings:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return Settings.model_validate(config)

settings = get_settings()

