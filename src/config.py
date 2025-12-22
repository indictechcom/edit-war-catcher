from dotenv import load_dotenv
import os

load_dotenv()

WIKI_API_URL = os.getenv("WIKI_API_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")
BOT_CONTACT = os.getenv("BOT_CONTACT")

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "editwar.duckdb")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
