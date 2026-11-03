# RevOpsIQ

RevOpsIQ is a full-stack B2B SaaS strategy and revenue operations intelligence platform built from the detailed project specification in `RevOpsIQ_Detailed_Project_Synopsis.pdf`.

## What is included
- Market intelligence with segment scoring and sizing assumptions
- Account intelligence and opportunity pipeline management
- Customer onboarding and adoption tracking
- Business review and action tracking
- Recommendation workflow driven by deterministic rules
- Shareable UI and persistent SQLite-backed data model for local development

## Local setup

### 1) Backend
```powershell
Set-Location 'C:\GEETHU\COLLEGE\PROJECTS\RevOpsIQ\backend'
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### 2) Frontend
```powershell
Set-Location 'C:\GEETHU\COLLEGE\PROJECTS\RevOpsIQ\frontend'
npm run dev
```

The Vite server is pinned to `127.0.0.1:5173` with `strictPort: true`. If that port is occupied, Vite exits with a port-in-use error instead of starting another instance on a different port.

## Environment
Copy `.env.example` to `.env` and adjust values as needed. The local CORS origin is `http://127.0.0.1:5173`, and the frontend calls the RevOpsIQ API at `http://127.0.0.1:8001/api`.

## Demo data
The backend seeds a fictional dataset for banking, marketplace and insurance segments, along with demo customers, opportunities, reviews and recommendations.

## Validation
Backend tests:
```bash
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

## Notes
- This is a demo portfolio project using synthetic data only.
- Postgres is the intended production architecture; SQLite is used as the local development fallback to keep the project runnable in this environment.
