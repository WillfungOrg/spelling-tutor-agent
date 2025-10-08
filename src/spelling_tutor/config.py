import os
from dotenv import load_dotenv


class Config:
    """Configuration class for environment variables."""

    def __init__(self):
        load_dotenv()

        self.livekit_url = os.getenv("LIVEKIT_URL")
        self.livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        self.livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")


def load_config() -> dict:
    """
    Load and validate environment variables from .env file.

    Returns:
        dict: Configuration dictionary with all required environment variables.

    Raises:
        ValueError: If any required environment variable is missing.
    """
    load_dotenv()

    required_keys = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
        "DEEPGRAM_API_KEY"
    ]

    config = {}
    missing_keys = []

    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        else:
            config[key] = value

    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

    return config


def get_db_path() -> str:
    """
    Get the database file path.

    Returns:
        str: Path to the SQLite database file.
    """
    return "data/spelling_tutor.db"