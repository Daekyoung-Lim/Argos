from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# .env is at project root (one level above backend/src/)
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    # Azure SQL Database
    azure_sql_db_server_name: str
    azure_sql_db_user_name: str
    azure_sql_db_password: str

    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str = "gpt-4.1"
    azure_openai_api_version: str = "2025-04-14"

    # Azure AI Vision
    azure_ai_vision_endpoint: str
    azure_ai_vision_api_key: str

    # Azure Blob Storage
    azure_storage_account_name: str
    azure_storage_account_key: str
    azure_storage_connection_string: str
    azure_storage_container_name: str = "asset-photos"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    @property
    def database_url(self) -> str:
        server = self.azure_sql_db_server_name
        user = self.azure_sql_db_user_name
        password = self.azure_sql_db_password
        driver = "ODBC+Driver+18+for+SQL+Server"
        return (
            f"mssql+pyodbc://{user}:{password}@{server}/argos-db"
            f"?driver={driver}&Encrypt=yes&TrustServerCertificate=no"
        )

    model_config = {
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
