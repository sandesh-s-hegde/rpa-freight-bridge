from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UIPATH_CLIENT_ID: str
    UIPATH_CLIENT_SECRET: str
    UIPATH_BASE_URL: str
    UIPATH_FOLDER_ID: str
    UIPATH_QUEUE_NAME: str
    API_SECRET_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
