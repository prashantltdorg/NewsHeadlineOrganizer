# Complete Setup Guide (Windows + VS Code)

## 1. Extract the project

1. Download `NewsHeadlineOrganizer.zip`.
2. Right-click it and choose **Extract All**.
3. Choose a convenient folder, for example `C:\Users\YourName\Projects`.
4. Open VS Code.
5. Select **File → Open Folder** and choose `NewsHeadlineOrganizer`.

## 2. Check Python

Open **Terminal → New Terminal** in VS Code and run:

```powershell
py --version
```

Use Python 3.10 or newer. If `py` is not recognized, install Python from https://www.python.org/downloads/ and select **Add Python to PATH** during installation.

## 3. Create a virtual environment

```powershell
py -m venv .venv
```

A `.venv` folder should appear in the project.

## 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell says script execution is disabled:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of the terminal prompt.

In VS Code, press `Ctrl+Shift+P`, select **Python: Select Interpreter**, and choose the interpreter inside this project's `.venv` folder.

## 5. Install project dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Wait until installation completes without errors.

## 6. Configure the news API key

The live-fetch feature uses NewsAPI.org.

1. Visit https://newsapi.org/ and create an account.
2. Copy your API key.
3. In the VS Code Explorer, copy `.env.example` and name the copy `.env`.
4. Open `.env` and replace the placeholder:

```env
NEWS_API_KEY=your_actual_api_key_here
```

5. Save the file.

The project automatically loads `.env` using `python-dotenv`, which is included in `requirements.txt`. Restart the server after changing the key.

**Alternative: set the key in the current PowerShell terminal**

```powershell
$env:NEWS_API_KEY="your_actual_api_key_here"
```

This setting applies only to that terminal session.

## 7. Start the application

```powershell
python -m uvicorn app:app --reload
```

You should see a message that Uvicorn is running on `http://127.0.0.1:8000`.

Open this address in Chrome or Edge:

http://127.0.0.1:8000

Do not close the terminal while using the application. To stop it, return to the terminal and press `Ctrl+C`.

## 8. First-time application walkthrough

1. Open the dashboard.
2. Select **Import / Export**.
3. Click **Load demo headlines** to populate sample records.
4. Open **Headlines** and test keyword/category search.
5. Open **Analytics** to view the category and date charts.
6. Open **Import / Export** and test CSV and JSON downloads.
7. Configure the API key, restart the server, and test **Fetch latest headlines**.

## 9. Common errors and fixes

### `py` or `python` is not recognized
Install Python and enable **Add Python to PATH**. Restart VS Code afterwards.

### `No module named fasthtml`
Activate `.venv`, then run:

```powershell
pip install -r requirements.txt
```

### PowerShell activation is blocked
Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Port 8000 is already in use
Run on another port:

```powershell
python -m uvicorn app:app --reload --port 8001
```

Then open http://127.0.0.1:8001.

### API key is missing
Check `.env` spelling and make sure you added `load_dotenv()` as explained above, or set `$env:NEWS_API_KEY` in the terminal. Restart the server.

### API returns an error
Check your API key, internet connection, API plan, endpoint access, and provider rate limits. The app should still display saved local data.

### Charts do not appear
Check that Matplotlib installed successfully:

```powershell
pip install matplotlib
```

Reload the Analytics page.

## 10. Important files

- `app.py`: FastHTML routes and user interface
- `news_service.py`: API client and category logic
- `storage.py`: JSON/CSV persistence, import, search and summary
- `charts.py`: Matplotlib visualizations
- `data/news_data.json`: stored headlines
- `requirements.txt`: dependencies
- `.env`: private API key; never upload it to GitHub

## 11. Run the project again later

Whenever you reopen the project:

```powershell
cd path\to\NewsHeadlineOrganizer
.\.venv\Scripts\Activate.ps1
python -m uvicorn app:app --reload
```

Then visit http://127.0.0.1:8000.
