"""Configuration management for the AI Research Assistant."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# API Keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# Model Configuration
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_MODELS = {
    "fast": "llama-3.1-8b-instant",
    "balanced": "mixtral-8x7b-32768",
    "powerful": "llama-3.1-70b-versatile"
}

# Timeout Settings
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "10"))

# Retry Configuration
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "1"))

# Storage Paths
CHROMA_DB_PATH: Path = Path(os.getenv("CHROMA_DB_PATH", "./chroma_db"))
CACHE_DIR: Path = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# LLM Configuration
MAX_CONTEXT_TOKENS: int = 4000
MAX_RESPONSE_TOKENS: int = 2000
TEMPERATURE: float = 0.7

# Tool Configuration
MAX_SEARCH_RESULTS: int = 3  # Reduced for faster processing
MAX_SCRAPE_LENGTH: int = 5000  # Reduced for faster processing
MAX_SUB_QUESTIONS: int = 5  # Limit sub-questions
MAX_URLS_TO_SCRAPE: int = 3  # Limit URLs to scrape
CHART_FORMAT: str = "png"  # png or svg

# Validation
def validate_config() -> bool:
    """Validate that required configuration is present."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is required. Set it in .env file.")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is required. Set it in .env file.")
    return True

