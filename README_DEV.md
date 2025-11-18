Development README
===================

Quick instructions to run the full stack locally using docker-compose or locally via yarn / uvicorn.

Prerequisites
- Docker & Docker Compose (optional for running containers)
- Node 18+/Yarn (for frontend dev)
- Python 3.11 and virtualenv (for backend dev)
- MongoDB running locally (or provide `MONGO_URI` pointing to a hosted Mongo)

Using docker-compose (recommended):

1. Copy environment variables:

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env to set MONGO_URI if needed
   ```

2. Start services:

   ```bash
   docker-compose up --build
   ```

3. Backend will be at `http://localhost:8000/api` and frontend expo web at `http://localhost:19006`.

Seeding voters into MongoDB (local Mongo, not Docker):

1. Activate a Python env and install requirements (backend):

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python scripts/seed_voters.py
   ```

2. If running via docker-compose and Mongo is remote, set `MONGO_URI` env var before `docker-compose up`.

Run frontend locally (without Docker):

```bash
cd frontend
yarn install
yarn start
```

Run backend locally (without Docker):

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Notes
- The `backend/scripts/seed_voters.py` reads `backend/seed/sample_voters_100.csv` and inserts rows into `voters` collection.
- The docker-compose file mounts your source into containers so you can continue editing code and see changes (backend uses --reload uvicorn).
