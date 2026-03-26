# Corva Automatic CSV Formatter

Cleans and reformats raw EDR CSV files for Corva stream ingestion. Supports NOV, Rigcloud, and Pason providers.

You do **not** need Cursor or any IDE—only **Python 3** and a terminal (Command Prompt, PowerShell, or Terminal).

## Run locally (any computer)

After you clone the repo or download and unzip it, open a terminal **in the project folder** (the one that contains `requirements.txt`).

### 1. Prerequisites

- **Python 3** installed (3.11 or 3.12 recommended). Download from [python.org](https://www.python.org/downloads/) if needed.

### 2. Virtual environment (recommended)

Using a virtual environment avoids permission issues and keeps dependencies separate from your system Python.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows** (if `python3` is not found, try `py -3`):

```bash
py -3 -m venv .venv
```

**Windows — activate:**

- Command Prompt: `.venv\Scripts\activate.bat`
- PowerShell: `.venv\Scripts\Activate.ps1`

You should see `(.venv)` at the start of your prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `pip` is not found, use:

```bash
python -m pip install -r requirements.txt
```

On Windows you can use `py -3 -m pip install -r requirements.txt`.

### 4. Start the app (choose one)

**Web app (easiest on unfamiliar machines—no Tk/GUI setup):**

```bash
python web/web_app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

**Desktop app (CustomTkinter GUI):**

```bash
python main.py
```

### Troubleshooting

| Issue | What to try |
|--------|-------------|
| `pip: command not found` | `python -m pip install -r requirements.txt` (or `py -3 -m pip ...` on Windows) |
| Desktop app: `No module named '_tkinter'` / `tkinter` (common with **Homebrew Python on Mac**) | Use the **web app** command above, **or** install Tk for your Python (e.g. Homebrew: `brew install python-tk@3.14` matching your Python version), then recreate the venv and reinstall. |
| Desktop app on **Linux** | Install Tk for your distro, e.g. Debian/Ubuntu: `sudo apt install python3-tk` |
| **Windows** + python.org installer | Tk is usually included; the desktop app often works out of the box. |

---

## Quick reference (if you already use a venv)

### Desktop app

```bash
pip install -r requirements.txt
python main.py
```

### Web app (local)

```bash
pip install -r requirements.txt
python web/web_app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Deploy to Render (free public URL)

1. Push this folder to a GitHub repo
2. Go to https://render.com and sign up / log in
3. Click "New" > "Web Service"
4. Connect your GitHub repo
5. Render auto-detects the config from `render.yaml`
6. Click "Create Web Service"
7. Your app will be live at your Render URL (e.g. `https://csv-cleaner-corva.onrender.com`)
