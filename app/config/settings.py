from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
LOGS_DIR = BASE_DIR / "logs"

DATABASE_PATH = DATA_DIR / "database.sqlite3"
ARTICLE_FILE_PATH = UPLOADS_DIR / "Articules.xlsx"
LOG_FILE_PATH = LOGS_DIR / "app.log"
