from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    PORT: int = 5003
    ML_PREDICTOR_URL: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()