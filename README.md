# Cooking Assistant

A responsive, strict domain-specific chatbot built with Python Flask and the Gemini API.

## Features

- Cooking-focused chatbot
- Gemini 3.6 Flash model
- No Firebase
- No database
- API key stored in `.env`
- Modern responsive cooking-themed UI
- English, Tamil and Tanglish friendly
- Unrelated questions are rejected
- Recipe steps, ingredients, substitutions and cooking troubleshooting
- Current-page chat only; no database persistence
- Runs on port `8000`
- Health endpoint at `/api/health`

## Project structure

```text
cooking-assistant/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## 1. Create virtual environment

### Windows PowerShell

```powershell
py -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, install directly:

```powershell
py -m pip install -r requirements.txt
```

## 2. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

## 3. Configure Gemini API

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder:

```text
GEMINI_API_KEY=your_real_api_key
```

The project is configured for:

```text
gemini-3.6-flash
```

## 4. Run

```powershell
py app.py
```

Open:

```text
http://127.0.0.1:8000
```

or:

```text
http://localhost:8000
```

## 5. Health check

Open:

```text
http://127.0.0.1:8000/api/health
```

## Important

Never put your real Gemini API key in frontend JavaScript or HTML.
Keep it in `.env` and do not commit `.env` to Git.

This project intentionally uses no Firebase and no database.
