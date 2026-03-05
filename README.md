# Venue Booking – Earliest Available Slot with Equipment

## Overview
You are implementing a scheduling service for a venue booking system. The venue has:
- **Rooms** (each with a unique string ID), and
- **Equipment items** (each with a unique string ID and an **equipment type** from `src/enums.py`).

Existing bookings reserve one room and zero or more equipment items for a time interval.

Your task is to implement the core scheduling algorithm, wrap it in a modular service design, and expose it via a small FastAPI application.

---

## Scheduling Problem
The core slot finder is a _pure_ function that, given the current state and a request, finds the **earliest available time slot** that meets the requirements.

### Inputs

**State**
- `rooms`: list of room IDs (e.g., `"room1"`, `"room2"`)
- `equipment`: mapping `equipment_type -> list[equipment_id]`  
  (e.g., `"projector" -> ["projector1", "projector2"]`)
- `booked_slots`: existing bookings, each containing:
  - `booking_id: str`
  - `room_id: str`
  - `start: ISO-8601 string`
  - `duration: int`
  - `equipment_ids: list[str]` (may be empty)

**Request**
- `earliest_start`: earliest start time (ISO-8601 string)
- `duration`: duration (minutes)
- `latest_end`: optional latest end bound (ISO-8601 string; `None` means no upper bound)
- `requested_equipment`: set of required equipment **types** (may be empty)

### Output
Return either:
- `(room_id, start_time, equipment_ids)` where:
  - `room_id` is the chosen room,
  - `start_time` is the start time as a `datetime`,
  - `equipment_ids` contains one chosen equipment item per required type,
- or `None` if no valid slot exists.

### Valid Slot Requirements
Find the **earliest** time `s` such that `[s, s+L)`:
- starts at or after `t`,
- ends **not later than** `e`, if provided (e.g. if `L` is 60 minutes, and `e` is 11:00, then the slot must end **by** 11:00, so the latest valid start time would be 10:00.),
- is available in **one** room for the full interval, and
- for each equipment type in `E`, has **at least one available equipment item** of that type for the full interval.

Tie-breaker:
- If multiple rooms are valid at the same earliest time, choose the room with the **lexicographically smallest** ID (e.g., `"room1" < "room2"`); same applies to equipment IDs.

---

## Example

Request:
```
t = 2026-01-10T20:10:00Z
L = 100
e = 2026-01-15T20:10:00Z
E = { microphone }
```

Interpretation:
Find the earliest 100-minute interval starting no earlier than Jan 10, 20:10 UTC and ending before Jan 15, 20:10 UTC, such that:
- a room is free for the full interval, and
- at least one microphone is free for the same interval (the chosen microphone is reserved for that booking).

---

## Deliverables

### 1) Core algorithm (unit-tested)
Implement the pure scheduling logic in `src/solver.py::Solver.find_available_slot(...)`

This method is the “brains” of the system and will be unit-tested directly for correctness and determinism.

### 2) Modular service + repository layer
Create an extendable structure around the solver:
- a **service layer** that orchestrates input/state retrieval and calls the solver,
- a **repository/data layer** (in-memory is fine) that stores rooms, equipment, and bookings.

Design with a future database in mind (storage should be behind an interface).

### 3) FastAPI wrapper
Implement a small FastAPI application that uses your service layer and exposes endpoints for:

- **Rooms**
  - `GET /rooms` (list rooms)
  - `POST /rooms` (add a room)
  - `DELETE /rooms/{room_id}` (remove a room)

- **Equipment**
  - `GET /equipment` (list equipment by type and IDs)
  - `POST /equipment` (add an equipment item)
  - `DELETE /equipment/{equipment_id}` (remove an equipment item)

- **Bookings**
  - `GET /bookings` (list bookings)
  - `POST /bookings` (create a booking; doesn't check, assumes a valid /availability call was made)
  - `DELETE /bookings/{booking_id}` (remove a booking)

- **Availability**
  - `POST /availability` (find earliest available slot; returns the proposed slot information or indicates no availability)

You do **not** need to implement authentication/authorization.

### 4) Runnable example
Your implementation should be runnable like the example in `main.py` using an in-memory repository. You may find some tests in `tests/` helpful as inspiration; expect that more similar tests will be run against your solution.


## Running Your App
We use `uv` for managing dependencies and running our services. Please create a `pyproject.toml` file and include everything we need to run and test your app.

Expect that we will

set up a virtual environment:
```sh
uv venv
source .venv/bin/activate
uv sync --all-groups
```

run tests:
```sh
uv run pytest
```

and start your FastAPI application:
```sh
uv run fastapi dev
```

---

## Notes & Assumptions
- Intervals are **half-open**: `[start, end)`.
- A booking ending at time `s` does **not** conflict with a booking starting at `s`.
- Equipment requirements are **any-of per type**: for each requested equipment type, any one free item of that type is sufficient.
- You may use third-party libraries if desired, but make sure to add them in `pyproject.toml`.
- You may use any (AI-) development tools you prefer.

---

## Tips
- Focus on: correctness, clear structure, testability, and readable code.
- Your solution does not need to be asymptotically optimal, but it should be sensible and deterministic.
- Use modern Python (3.13+) conventions and type annotations throughout.
