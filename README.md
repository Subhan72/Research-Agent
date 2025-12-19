# 🔍 ResearchAgent

<div align="center">

**An AI-Powered Autonomous Research Assistant with Multi-Tool Orchestration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Transform any research question into a comprehensive, cited report in minutes*

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

**ResearchAgent** is an intelligent, autonomous research system that leverages Large Language Models (LLMs) to break down complex queries, search the web, extract knowledge, analyze data, and generate professional research reports with citations—all automatically.

Unlike traditional search engines, ResearchAgent doesn't just find information—it **plans**, **executes**, **synthesizes**, and **presents** comprehensive research findings in a structured, academic-style report.

### 🎯 Key Capabilities

- **🧠 Intelligent Planning**: Automatically breaks queries into 3-7 focused sub-questions
- **🌐 Web Search Integration**: Uses Tavily API for intelligent web searching
- **📄 Content Extraction**: Scrapes and cleans webpage content automatically
- **📊 Data Analysis**: Extracts numbers, creates tables, and generates visualizations
- **📝 Report Generation**: Produces structured Markdown reports with citations
- **💾 Smart Caching**: JSON and vector-based caching for efficiency
- **🎨 Modern UI**: Beautiful Streamlit interface with real-time progress

---

## ✨ Features

### Core Functionality

- ✅ **Autonomous Research Workflow**: End-to-end automation from query to report
- ✅ **Multi-Tool Orchestration**: Seamlessly coordinates web search, scraping, analysis, and synthesis
- ✅ **Structured Report Generation**: Creates professional reports with:
  - Executive Summary
  - Key Findings
  - Deep Dive Analysis
  - Data Tables & Charts
  - Conclusion
  - References with URLs
- ✅ **PDF Export**: Convert reports to PDF format
- ✅ **Semantic Caching**: ChromaDB vector store for intelligent result caching
- ✅ **Error Handling**: Robust retry logic and graceful error recovery

### Technical Highlights

- 🚀 **Fast Performance**: Optimized for 2-4 minute research cycles
- 🔒 **Secure**: Input validation and sanitization
- 📦 **Modular Architecture**: Clean separation of concerns
- 🧪 **Tested**: Unit and integration tests included
- 📚 **Well Documented**: Comprehensive code documentation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│                    (Streamlit Frontend)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                           │
│              (RESTful API + Streaming)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   Planner    │ │  Executor   │ │ Synthesizer │
│              │ │             │ │             │
│ • Breaks     │ │ • Orchestrates│ │ • Generates │
│   queries    │ │   tools      │ │   reports   │
│ • Creates    │ │ • Handles    │ │ • Formats   │
│   plan       │ │   errors     │ │   citations │
└───────┬──────┘ └──────┬───────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Web Search  │ │   Scraper   │ │ Data Analyzer│
│  (Tavily)   │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

### System Components

1. **Planner**: Uses Groq LLM to break queries into sub-questions and create execution plans
2. **Executor**: Orchestrates tool execution sequentially with error handling
3. **Synthesizer**: Aggregates findings and generates structured reports
4. **Tools Layer**: Modular tools for search, scraping, analysis, calculation, and summarization
5. **Storage Layer**: JSON caching and ChromaDB vector store for semantic search

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com))
- Tavily API key ([Get one here](https://tavily.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/researchagent.git
   cd researchagent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   python setup_env.py
   # Edit .env and add your API keys:
   # GROQ_API_KEY=your_key_here
   # TAVILY_API_KEY=your_key_here
   ```

5. **Start the backend**
   ```bash
   uvicorn backend.main:app --reload
   ```
   Backend runs on `http://localhost:8000`

6. **Start the frontend** (in a new terminal)
   ```bash
   streamlit run frontend/app.py
   ```
   Frontend opens at `http://localhost:8501`

### First Research Query

1. Open `http://localhost:8501` in your browser
2. Enter a research question (e.g., "Impact of AI on Pakistani job market")
3. Click "Start Research"
4. Wait 2-4 minutes for the complete report
5. Download as Markdown or PDF

---

## 📖 Usage Examples

### Example Queries

- "Latest developments in quantum computing"
- "Climate change effects on agriculture in 2024"
- "Comparison of renewable energy sources"
- "Machine learning applications in healthcare"
- "Impact of remote work on productivity"

### API Usage

#### Synchronous Research
```python
import requests

response = requests.post(
    "http://localhost:8000/agent/research/sync",
    json={
        "query": "Impact of AI on job market",
        "generate_pdf": False,
        "use_cache": True
    }
)

result = response.json()
print(result['report']['markdown'])
```

#### Streaming Research
```python
import requests

response = requests.post(
    "http://localhost:8000/agent/research",
    json={"query": "Your research question"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

---

## 🔧 Configuration

Customize behavior in `config.py` or via environment variables:

```python
# Performance Tuning
MAX_SEARCH_RESULTS = 3        # Results per search
MAX_SUB_QUESTIONS = 5         # Max sub-questions
MAX_URLS_TO_SCRAPE = 3        # URLs to scrape
MAX_SCRAPE_LENGTH = 5000      # Text length limit

# Model Selection
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast model
# Alternatives: "mixtral-8x7b-32768", "llama-3.1-70b-versatile"

# Timeouts
API_TIMEOUT = 30              # API call timeout
SCRAPER_TIMEOUT = 10          # Web scraping timeout
```

---

## 📚 API Documentation

### Endpoints

#### `POST /agent/research`
Streaming research endpoint (Server-Sent Events)

**Request:**
```json
{
  "query": "Your research question",
  "generate_pdf": false,
  "use_cache": true
}
```

#### `POST /agent/research/sync`
Synchronous research endpoint

**Response:**
```json
{
  "query": "Your question",
  "plan": {...},
  "tool_results": [...],
  "report": {
    "markdown": "# Report...",
    "citations": [...]
  },
  "success": true
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Research Assistant API"
}
```

Full API documentation available at `http://localhost:8000/docs` when the server is running.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Groq**: High-performance LLM inference
- **Tavily**: Intelligent web search API
- **ChromaDB**: Vector database for semantic caching
- **BeautifulSoup4**: Web scraping
- **Pandas/NumPy**: Data analysis

### Frontend
- **Streamlit**: Interactive web interface
- **Plotly/Matplotlib**: Data visualization

### Infrastructure
- **Uvicorn**: ASGI server
- **Python-dotenv**: Environment management
- **Tenacity**: Retry logic

---

## 📁 Project Structure

```
researchagent/
├── backend/
│   ├── agent/           # Core agent modules
│   │   ├── planner.py    # Query planning
│   │   ├── executor.py   # Tool orchestration
│   │   ├── synthesizer.py # Report generation
│   │   └── research_agent.py # Main agent
│   ├── tools/           # Research tools
│   │   ├── web_search.py
│   │   ├── scraper.py
│   │   ├── data_analysis.py
│   │   ├── calculator.py
│   │   └── summarizer.py
│   ├── storage/         # Caching & storage
│   │   ├── cache.py
│   │   └── vector_store.py
│   ├── utils/           # Utilities
│   │   ├── llm_client.py
│   │   └── validators.py
│   └── main.py          # FastAPI app
├── frontend/
│   ├── app.py           # Streamlit main app
│   └── components/      # UI components
├── tests/               # Test suite
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── README.md            # This file
```

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_tools.py

# Run with coverage
python -m pytest --cov=backend tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure all tests pass** (`python -m pytest`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all modules and functions
- Add tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast LLM inference
- [Tavily](https://tavily.com/) for intelligent web search
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Streamlit](https://streamlit.io/) for the beautiful UI framework

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/researchagent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/researchagent/discussions)

---

<div align="center">

**Made with ❤️ by the ResearchAgent Team**

⭐ Star this repo if you find it useful!

</div>

