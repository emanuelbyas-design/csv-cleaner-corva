# CSV Cleaner for Corva

Cleans and reformats raw EDR CSV files for Corva stream ingestion. Supports NOV, Rigcloud, and Pason providers.

## Desktop App

```bash
pip install -r requirements.txt
python main.py
```

## Web App (local)

```bash
pip install -r requirements.txt
python web/web_app.py
```

Then open http://localhost:5000 in your browser.

## Deploy to Render (free public URL)

1. Push this folder to a GitHub repo
2. Go to https://render.com and sign up / log in
3. Click "New" > "Web Service"
4. Connect your GitHub repo
5. Render auto-detects the config from `render.yaml`
6. Click "Create Web Service"
7. Your app will be live at `https://csv-cleaner-corva.onrender.com`
