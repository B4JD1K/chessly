from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://chessly:chessly@localhost:5432/chessly"
    environment: str = "development"
    debug: bool = True

    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"

    # Discord OAuth2
    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_redirect_uri: str = "http://localhost:3000"

    # Stockfish
    stockfish_path: str = "/usr/bin/stockfish"

    class Config:
        env_file = ".env"


settings = Settings()
