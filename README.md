# Airline Itinerary Reconstruction

Django + DRF backend that rebuilds a traveller's itinerary from a set of flight
tickets. The traveller always departs from `JFK`, every ticket is used exactly
once, and when several itineraries are valid the lexically smallest is returned
(LeetCode 332).

A modular monolith with two apps:

| App | Responsibility |
|-----|----------------|
| `apps/tickets` | Accept, validate, store and retrieve tickets (grouped in batches) |
| `apps/itineraries` | Graph building, Hierholzer's algorithm, route validation, itinerary persistence and status |

## Workflow

1. Client `POST`s tickets -> validated and stored as a **batch**.
2. Client `POST`s the `batch_id` to reconstruct.
3. Graph builder creates a sorted adjacency list.
4. Itinerary builder runs Hierholzer's algorithm (lexically smallest first).
5. Validator checks the route starts at JFK and uses every ticket exactly once.
6. Itinerary is saved (`COMPLETED` or `FAILED`) and returned.

## Run with Docker

```bash
docker compose up --build
```

API is served at http://localhost:8000.

## Run locally (no Postgres needed)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DB_ENGINE=sqlite
python manage.py migrate
python manage.py runserver
```

## Tests

```bash
DB_ENGINE=sqlite pytest          # local, SQLite
docker compose run --rm web pytest   # against PostgreSQL
```

## API

### `POST /api/v1/tickets/`

```json
{ "tickets": [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]] }
```
`201` ->
```json
{ "batch_id": "<uuid>", "ticket_count": 5, "tickets": [["JFK","SFO"], "..."], "created_at": "..." }
```
`400` on invalid input (1-300 tickets, each `[from, to]` of 3 uppercase letters, `from != to`).

### `GET /api/v1/tickets/?batch_id=<uuid>`
Retrieve a submitted batch. `404` if unknown.

### `POST /api/v1/itineraries/reconstruct/`

```json
{ "batch_id": "<uuid>" }
```
- `201` new itinerary, `200` an existing completed itinerary for that batch (idempotent)
- `422` tickets cannot form a valid itinerary from JFK (itinerary saved with status `FAILED`)
- `404` unknown batch

```json
{
  "id": "<uuid>",
  "batch_id": "<uuid>",
  "status": "COMPLETED",
  "route": ["JFK","ATL","JFK","SFO","ATL","SFO"],
  "error_message": "",
  "created_at": "...",
  "completed_at": "..."
}
```

### `GET /api/v1/itineraries/{id}/`
Retrieve an itinerary and its status (`PENDING`, `COMPLETED`, `FAILED`).

## Algorithm notes

- `graph_builder.py` stores each airport's destinations sorted in descending
  order so the smallest is an O(1) `pop()`; duplicate tickets stay as separate edges.
- `itinerary_builder.py` is an iterative Hierholzer: walk to the smallest unused
  destination, append airports in post-order, reverse at the end. O(E log E).
- `validators.py` is a safety net: confirms the start airport, route length and
  that the multiset of legs equals the multiset of tickets.

## Design decisions

- Authentication is intentionally omitted (no user management in scope); add
  DRF auth/permission classes in `config/settings.py` if needed.
- Reconstruction is synchronous; with <= 300 tickets it completes in
  milliseconds, so no Celery/Kafka/RabbitMQ is needed.
