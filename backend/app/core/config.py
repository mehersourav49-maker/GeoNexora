from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "GeoNexora"
    database_url: str = "sqlite:///./geonexora.db"
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
