# Route Optimizer

A full-stack route optimization web app built with FastAPI, React, Leaflet, OpenStreetMap, and the public OSRM API.

## Project Structure

```text
.
|-- app
|   |-- main.py
|   |-- models
|   |-- routes
|   |-- services
|   `-- utils
|-- frontend
|   |-- public
|   `-- src
|-- requirements.txt
`-- README.md
```

## Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://127.0.0.1:5173`.

## Environment Configuration

By default, the frontend uses the Vite proxy and sends API requests to `/api`.

To point the frontend at another backend URL, create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Contract

`POST /optimize-route`

Request:

```json
{
  "locations": [[28.6139, 77.209], [19.076, 72.8777], [12.9716, 77.5946]]
}
```

Response:

```json
{
  "optimal_route": [[28.6139, 77.209], [21.1458, 79.0882], [19.076, 72.8777]],
  "total_distance_km": 1458.251
}
```

## Notes

- Maximum 10 locations per request to keep OSRM usage safe and responsive.
- Pairwise distance requests are cached in memory to reduce repeated API calls.
- If OSRM geometry fails, the backend still returns the ordered stop list and total distance.
