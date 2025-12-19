"""Helper script to create .env file from template."""
import os
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print(".env file already exists. Skipping creation.")
        return
    
    # Create .env.example if it doesn't exist
    if not env_example_path.exists():
        env_example_content = """# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Tavily API Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# ChromaDB Configuration (optional)
CHROMA_DB_PATH=./chroma_db

# Model Configuration
GROQ_MODEL=llama-3.1-8b-instant

# Timeout Settings (seconds)
API_TIMEOUT=30
SCRAPER_TIMEOUT=10

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY=1
"""
        env_example_path.write_text(env_example_content)
        print(f"Created {env_example_path}")
    
    # Copy .env.example to .env
    if env_example_path.exists():
        env_path.write_text(env_example_path.read_text())
        print(f"Created {env_path} from template.")
        print("Please edit .env and add your API keys!")
    else:
        print("Error: Could not find .env.example template.")

if __name__ == "__main__":
    create_env_file()

