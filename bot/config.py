import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


config = Config()
