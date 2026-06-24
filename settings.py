"""Environment configuration for the IngredientAI API.

All secrets come from env vars (Railway variables / local .env). Nothing committed.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase (DB / auth / pgvector)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Cloudflare R2 (image bytes)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "ingredientai-images"

    # API behaviour
    cors_origins: str = "*"
    environment: str = "development"


settings = Settings()
