from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    database_url: str
    confidence_threshold: float = 0.75

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
