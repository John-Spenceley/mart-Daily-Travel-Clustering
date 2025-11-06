
# Smart-Daily-Travel-Clustering

A minimal, ready-to-merge **Smart Daily Travel Clustering** feature pack.

- **Backend (FastAPI)** exposes `/optimize/cluster` to:
  - cluster POIs by proximity (radius-km)
  - greedily order within clusters
  - pack items into day schedules between `start_time` and `end_time`
- **Frontend (Vite + React)** gives a toggle for clustering, radius slider, transport mode, and renders clustered days with distance/time badges.

No API keys. No external services.

---

## Quickstart

### Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
# API: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

---

## How to merge into another repo

**Backend**
1. Copy `backend/helpers/clustering.py` into your project (e.g., `helpers/` or `app/utils/`).
2. Copy `backend/services/optimize.py` into your routers/services folder.
3. In your FastAPI `main.py`:
   ```python
   from services import optimize
   app.include_router(optimize.router)
   ```
4. Ensure CORS allows your frontend origin.

**Frontend**
- Copy these and merge with your UI:
  - `frontend/src/components/SearchForm.jsx`
  - `frontend/src/components/Itinerary.jsx`
  - `frontend/src/App.jsx` (or integrate the handler bits)

---

## Roadmap (optional)
- Replace rough travel time with Google Directions.
- Add Leaflet map per day.
- Budget engine + personality modes before clustering.
