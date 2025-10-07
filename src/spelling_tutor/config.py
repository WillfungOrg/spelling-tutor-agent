import os
from dotenv import load_dotenv


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