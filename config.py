from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # S3 Configuration
    s3_region: str = "ir-thr-at1"
    s3_bucket_name: str
    s3_endpoint_url: str
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    
    
    max_upload_size_bytes: int = 5 * 1024 * 1024 # 5MB
    
    posts_per_page: int = 10
    
    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 2525
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True
    
    frontend_url: str = "http://localhost:8000"
    
    
settings = Settings()  # type: ignore[call-arg] # Loaded from .env file