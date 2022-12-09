from pydantic import BaseSettings

"""
Config file for server and database.
@Author : David GEORGES
"""

class ServerSettings(BaseSettings):
    HOST : str
    PORT : str

class DatabaseSettings(BaseSettings):
    DB_URL : str
    DB_NAME : str

class TokenSettings(BaseSettings):
    JWT_ACCESS_TOKEN_SECRET : str
    JWT_REFRESH_TOKEN_SECRET : str
    JWT_ALGORITHM : str
    JWT_REFRESH_TOKEN_EXPIRES_IN : int
    JWT_ACCESS_TOKEN_EXPIRES_IN : int
    
class EmailSettings(BaseSettings):
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_PORT : str
    MAIL_SERVER : str
    MAIL_TLS=True,
    MAIL_SSL=False,
    MAIL_SECRET_KEY_RESET_PASSWORD : str
    USE_CREDENTIALS=True,

class Settings(ServerSettings,DatabaseSettings,EmailSettings,TokenSettings):
    class Config:
        env_file = 'local.env'
        env_file_encoding = 'utf-8'

settings = Settings()   