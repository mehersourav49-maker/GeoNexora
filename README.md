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
VITE_API_URL= "https://geonexora.onrender.com"

The simulation endpoint is intentionally in-memory and does not create an alert. The engineering calculations are screening estimates for decision support, not certified hydraulic/geotechnical models.

## Enhanced hydrology, resilience and replay features

This branch adds an SCS Curve Number runoff-depth calculation, AMC-I/II/III empirical CN conversion, an SCS peak-flow screening estimate, Manning-equation corridor travel-time estimates, deterministic feature attribution, simulated sensor backhaul failover, an illustrative Chamoli replay, a Service Worker queue for failed telemetry POSTs, hazard corridor styling, shelter capacity meters, and CAP-compatible JSON/XML advisory exports.

### Important deployment notes

- Existing sensor databases receive an additive `transmission_mode` column at API startup when absent. Back up the Render PostgreSQL database before deploying any schema-changing build.
- `POST /api/v1/monitoring/simulate-backhaul-failure?failed=true` simulates channel-state changes only; it does not control physical 4G or LoRa hardware. Restore with `failed=false`.
- Replay endpoint: `/api/v1/analytics/replay/chamoli-2021`. Its ten telemetry points are **reconstructed demonstration data**, not historical sensor observations. No 54-minute detection claim is asserted.
- Manning travel times use illustrative segment lengths, roughness, hydraulic radii, and slopes. Replace these with surveyed/channel-gauge inputs and calibrate against observed flood waves before operational use.
- SCS-CN results are screening calculations; provide a basin-specific CN, event rainfall depth/duration, and time of concentration. A simple triangular hydrograph is shown for visualization and is not a calibrated routing model.
- CAP export is a draft alert document. It does not transmit real SMS/WhatsApp messages or constitute an official warning. Validate CAP fields and authorization procedures with the responsible disaster-management agency.
- The Service Worker can queue failed browser-originated telemetry POSTs to IndexedDB and retry them when online; it does not replace durable field-device storage or a tested radio mesh. Service Workers require HTTPS (or localhost).

### Added API routes

- `POST /api/v1/monitoring/simulate-backhaul-failure?failed=true|false`
- `GET /api/v1/monitoring/transmission-modes`
- `GET /api/v1/analytics/replay/chamoli-2021`
- Backward-compatible replay alias: `GET /api/analytics/replay/chamoli-2021`
