from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str
    bot_token: str = ""
    admin_username: str = "admin"
    admin_password: str = "change_me"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()