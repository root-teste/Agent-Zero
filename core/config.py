import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("SYSTEM_API_KEY")
    API_URL = os.getenv("API_URL")

settings = Settings()
