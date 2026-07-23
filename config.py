import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "vocab-app-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'vocab.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
    # Words per study session
    WORDS_PER_SESSION = 20
    # New words to introduce per day
    NEW_WORDS_PER_DAY = 10
