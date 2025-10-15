<p>
  <img src="./images/logo.png" alt="logo" width="64" style="vertical-align: middle; margin-right: 12px;">
  <span style="vertical-align: middle;">This is the description text that appears to the right of the image.</span>
</p>


# 🧠 Smart Task Planner AI

An intelligent web application that uses Google's Gemini AI to break down high-level goals into a detailed, actionable project plan.
This project features a full-stack implementation with a Flask backend, a SQLite database, and a responsive web interface.

## ✨ Features

* **AI-Powered Planning**: Leverages the Gemini Pro model to generate logical and comprehensive task breakdowns.
* **Interactive Web Interface**: A clean and user-friendly frontend built with HTML, CSS, and JavaScript for submitting goals and viewing plans.
* **Database Persistence**: Automatically saves every generated plan to a SQLite database for future reference.
* **Structured JSON API**: A robust backend API that provides plans in a clean, predictable JSON format.
* **Dynamic Results**: Displays generated tasks instantly on the webpage without needing a refresh.

## 🛠️ Technical Stack

* **Backend**: Python, Flask
* **Database**: SQLite
* **AI Model**: Google Gemini Pro
* **Frontend**: HTML5, CSS3, JavaScript
* **Deployment**: Gunicorn / Waitress (Production-ready)

# Smart Task Planner AI

An intelligent web application that uses Google Gemini API to turn high-level goals into detailed, actionable project plans. This repository includes a small Flask backend, a simple JavaScript front-end, and a SQLite database to persist generated plans.

> NOTE: This README intentionally does NOT include any API keys. Keep secrets in a `.env` file or your environment.

## Features

- AI-powered plan generation using Google Gemini
- Save and view previously generated plans in `plans.db` (SQLite)
- Simple web UI with instant results
- Small API (POST /create-plan, GET /plans, GET /plans/<id>)

## Requirements

- Python 3.8+
- pip
- A Google AI API key (for production mode)

## Quickstart

1. Clone the repo:

```powershell
git clone https://github.com/Yathnika/SMART-TASK-PLANNER.git
cd smart-task-planner
```

2. (Optional) Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1  # PowerShell
# or: venv\Scripts\activate.bat  # cmd.exe
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your key (example):

```
# .env (DO NOT COMMIT)
GOOGLE_API_KEY=your_real_api_key_here
```

5. Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Local development without using the AI (no quota consumption)

If you want to develop the UI or test the app without calling the external API, set the environment variable `DISABLE_AI=1` before running the server. The server will return a small dummy plan and still save it to the DB so you can test the full flow.

PowerShell example:

```powershell
$env:DISABLE_AI = '1'
python app.py
```

## Inspecting the saved plans (plans.db)

- The SQLite database `plans.db` is created in the project root when the app first runs.
- I added a helper script `scripts/inspect_db.py` to list and show plans:

```powershell
# List saved plans (latest 50)
python .\scripts\inspect_db.py list

# Show JSON for plan id 3
python .\scripts\inspect_db.py show 3
```

You can also open `plans.db` in any SQLite GUI tool (DB Browser for SQLite) if you prefer a graphical view.

## API Endpoints

- `POST /create-plan` — JSON body: `{ "goal": "Your goal text" }`. Returns the generated plan.
- `GET /plans` — Renders an HTML page listing saved plans.
- `GET /plans/<id>` — Returns JSON for a saved plan by id.

## Error handling & quotas

- If the Gemini API returns a quota or rate limit error, the server will now return an HTTP 429 with the API message. Check server logs for the raw model response in `last_raw_model_response.txt` when parsing fails.

## Contributing / Security

- Do NOT commit your `.env` file or API keys. Add `.env` to `.gitignore`.
- If you want to test without API calls, use `DISABLE_AI=1` as shown above.

