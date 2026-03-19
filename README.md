# Coiled Tubing Reel Calculator

A small Streamlit web app for estimating coiled tubing reel windings and capacity.

## Features

- Calculate turns per layer, radial layers, and total windings
- Calculate reel capacity from geometry
- Calculate required outer wound diameter for a target tubing length
- Metric and inch-friendly input options
- Adjustable winding pitch factor for more conservative packing estimates

## Run locally

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push these files to a GitHub repo.
2. Sign in to Streamlit Community Cloud.
3. Choose **New app**.
4. Select your GitHub repo, branch, and `app.py` as the entrypoint.
5. Deploy.

## Deploy on Render

Use a Python web service with:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Files

- `app.py` – the Streamlit application
- `requirements.txt` – Python dependencies
- `README.md` – usage and deployment instructions
