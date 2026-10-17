from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str
    app_name: str = "AI Meeting Minutes"
    admin_api_key: str = "meeting_admin_test_12345"

    claude_model: str = "claude-haiku-4-5"
    max_tokens: int = 4096

    free_limit: int = 3
    basic_limit: int = 30
    pro_limit: int = 100
    business_limit: int = 10000


settings = Settings()