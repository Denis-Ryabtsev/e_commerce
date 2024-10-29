from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_PASS: str
    DB_USER: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@\
            {self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


setting = Setting()