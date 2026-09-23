# GeoNexora

Production-oriented prototype for hyper-local flash-flood early warning and incident command.

## Run backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed_demo_data.py
python -m uvicorn app.main:app --reload --port 8000
```

## Run frontend
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

Set `VITE_API_URL` if the API is not on http://127.0.0.1:8000.

The simulation endpoint is intentionally in-memory and does not create an alert. The engineering calculations are screening estimates for decision support, not certified hydraulic/geotechnical models.
