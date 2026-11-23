# News Headline Organizer

A local-first Python application built with **FastHTML**. It fetches headlines from NewsAPI.org, classifies them, stores them in JSON, supports keyword/category search, imports CSV, exports CSV/JSON, and generates Matplotlib charts.

## Requirements

- Python 3.10 or newer
- Internet connection for API fetching and first-time dependency installation
- A NewsAPI.org API key for live headlines (optional; demo data works without it)

## Windows setup (PowerShell)

```powershell
# 1. Open this project folder in VS Code.
cd path\to\NewsHeadlineOrganizer

# 2. Create a virtual environment.
py -m venv .venv

# 3. Activate it.
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation, run this once in the current terminal:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Then activate again:
.\.venv\Scripts\Activate.ps1

# 4. Install packages.
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Create your local environment file.
Copy-Item .env.example .env
# Open .env and replace the placeholder with your API key.

# 6. Start the web application.
python -m uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** in your browser. Keep the terminal running while using the app. Press `Ctrl+C` to stop it.

## macOS / Linux setup

```bash
cd NewsHeadlineOrganizer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add NEWS_API_KEY
python -m uvicorn app:app --reload
```

## Configure NewsAPI

1. Create an account at https://newsapi.org/.
2. Obtain an API key from your account dashboard.
3. Copy `.env.example` to `.env`.
4. Set `NEWS_API_KEY=your_actual_key` in `.env`.
5. Restart the server.

**Important:** This starter project reads environment variables from the process environment. To load `.env` automatically, install `python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` near the top of `app.py`, or set the environment variable in your terminal before starting Uvicorn. See the detailed setup guide for the simplest option.

NewsAPI plan limitations, availability of country/category filters, attribution rules, and development/production usage restrictions are determined by NewsAPI. Check its current terms before public deployment.

## Features

- FastHTML web interface with responsive CSS
- Live top-headlines API integration
- Keyword-based category classification
- JSON local persistence with recovery from malformed JSON
- Keyword and category filtering
- CSV import with row validation and duplicate avoidance
- CSV and JSON downloads
- Executive summary metrics
- Matplotlib category and timeline charts
- Demo dataset for offline UI testing

## Data locations

- `data/news_data.json`: primary local dataset (created automatically)
- `reports/`: generated CSV/JSON exports
- `static/`: generated chart images

## Notes

- Demo records use example.com links and are illustrative, not live news.
- Category assignment is a transparent keyword heuristic, not an AI classifier.
- Do not commit `.env` or a real API key to GitHub.
- Before production deployment, add authentication, rate limiting, stronger URL validation, and API-provider compliance checks.
