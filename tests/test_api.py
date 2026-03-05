import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app
from src.api.v1.routes import booking_db

client = TestClient(app)

# ---------------- Fixture to reset DB ----------------
@pytest.fixture(autouse=True)
def reset_db():
    # Clear rooms, equipment, bookings before each test
    booking_db._rooms.clear()
    booking_db._equipment.clear()
    booking_db._bookings.clear()

# helper for datetime to iso
def iso(dt: datetime) -> str:
    return dt.isoformat()

# ------------------ Rooms ------------------

def test_rooms_add_and_list():
    # initially empty
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == []

    # add a room
    response = client.post("/rooms", json={"room_id": "room1"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # add duplicate room
    response = client.post("/rooms", json={"room_id": "room1"})
    assert response.status_code == 400

    # add another room
    response = client.post("/rooms", json={"room_id": "room2"})
    assert response.status_code == 200

    # list rooms should be sorted lexicographically
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json() == ["room1", "room2"]

def test_rooms_delete():
    client.post("/rooms", json={"room_id": "room3"})
    response = client.delete("/rooms/room3")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # delete non-existing room
    response = client.delete("/rooms/nonexistent")
    assert response.status_code == 200  # graceful
    assert response.json()["status"] == "success"

# ------------------ Equipment ------------------

def test_equipment_add_and_list():
    # initially empty
    response = client.get("/equipment")
    assert response.status_code == 200
    eq = response.json()
    assert isinstance(eq, dict)

    # add equipment
    response = client.post("/equipment", json={"equipment_id": "p1", "equipment_type": "projector"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # add duplicate equipment
    response = client.post("/equipment", json={"equipment_id": "p1", "equipment_type": "projector"})
    assert response.status_code == 400

    # add another equipment
    response = client.post("/equipment", json={"equipment_id": "p2", "equipment_type": "projector"})
    assert response.status_code == 200

    # list equipment should include sorted list
    response = client.get("/equipment")
    data = response.json()
    assert data["projector"] == ["p1", "p2"]

def test_equipment_delete():
    client.post("/equipment", json={"equipment_id": "w1", "equipment_type": "whiteboard"})
    response = client.delete("/equipment/w1")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # delete non-existing equipment
    response = client.delete("/equipment/nonexistent")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# ------------------ Bookings ------------------

def test_booking_create_and_list():
    # setup: room and equipment
    client.post("/rooms", json={"room_id": "roomA"})
    client.post("/equipment", json={"equipment_id": "m1", "equipment_type": "microphone"})

    # create booking
    start = datetime(2026, 3, 1, 10, 0)
    response = client.post("/bookings", json={
        "booking_id": "book1",
        "room_id": "roomA",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": ["m1"]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # duplicate booking ID
    response = client.post("/bookings", json={
        "booking_id": "book1",
        "room_id": "roomA",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": []
    })
    assert response.status_code == 400

    # non-existent room
    response = client.post("/bookings", json={
        "booking_id": "book2",
        "room_id": "nonexistent",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": []
    })
    assert response.status_code == 400

    # non-existent equipment
    response = client.post("/bookings", json={
        "booking_id": "book3",
        "room_id": "roomA",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": ["fake_eq"]
    })
    assert response.status_code == 400

    # list bookings
    response = client.get("/bookings")
    data = response.json()
    assert any(b["booking_id"] == "book1" for b in data)

def test_booking_delete():
    # setup
    client.post("/rooms", json={"room_id": "roomDel"})
    start = datetime(2026, 3, 2, 10, 0)
    client.post("/bookings", json={
        "booking_id": "del1",
        "room_id": "roomDel",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": []
    })

    # delete booking
    response = client.delete("/bookings/del1")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # delete non-existent
    response = client.delete("/bookings/nonexistent")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# ------------------ Availability ------------------

def test_availability_no_bookings():
    client.post("/rooms", json={"room_id": "room0"})
    client.post("/equipment", json={"equipment_id": "m0", "equipment_type": "microphone"})

    start = datetime(2026, 3, 1, 8, 0)
    response = client.post("/availability", json={
        "earliest_start": iso(start),
        "duration": 30,
        "latest_end": None,
        "requested_equipment": ["microphone"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["room_id"] == "room0"
    assert data["equipment_ids"] == ["m0"]

def test_availability_partial_booked():
    # Setup
    client.post("/rooms", json={"room_id": "a_room1"})
    client.post("/rooms", json={"room_id": "a_room2"})
    client.post("/equipment", json={"equipment_id": "a_m1", "equipment_type": "microphone"})

    # book room2/m1
    start = datetime(2026, 3, 1, 10, 0)
    client.post("/bookings", json={
        "booking_id": "b1",
        "room_id": "a_room2",
        "start": iso(start),
        "duration": 60,
        "equipment_ids": ["a_m1"]
    })

    # check availability before booking
    avail_start = datetime(2026, 3, 1, 8, 0)
    response = client.post("/availability", json={
        "earliest_start": iso(avail_start),
        "duration": 30,
        "latest_end": None,
        "requested_equipment": ["microphone"]
    })

    data = response.json()
    assert data["available"] is True
    assert data["room_id"] == "a_room1"  # room1 free
    assert "a_m1" in data["equipment_ids"] or len(data["equipment_ids"]) == 0

def test_availability_fully_booked():
    # only one room/equipment
    client.post("/rooms", json={"room_id": "room0"})
    client.post("/equipment", json={"equipment_id": "m0", "equipment_type": "microphone"})

    # book it fully
    start = datetime(2026, 3, 1, 10, 0)
    client.post("/bookings", json={
        "booking_id": "full1",
        "room_id": "room0",
        "start": iso(start),
        "duration": 120,
        "equipment_ids": ["m0"]
    })

    # request during same time
    request_start = datetime(2026, 3, 1, 10, 30)
    response = client.post("/availability", json={
        "earliest_start": iso(request_start),
        "duration": 60,
        "latest_end": iso(datetime(2026, 3, 1, 11, 30)),
        "requested_equipment": ["microphone"]
    })
    data = response.json()
    assert data["available"] is False

    # request during same time but no end time
    request_start = datetime(2026, 3, 1, 10, 30)
    response = client.post("/availability", json={
        "earliest_start": iso(request_start),
        "duration": 60,
        "latest_end": None,
        "requested_equipment": ["microphone"]
    })
    data = response.json()
    assert data["available"] is True
    assert data["start"] == "2026-03-01T12:00:00"

def test_availability_nonexistent_equipment():
    response = client.post("/availability", json={
        "earliest_start": iso(datetime(2026, 3, 1, 8, 0)),
        "duration": 30,
        "latest_end": None,
        "requested_equipment": ["FAKE_EQ"]
    })
    assert response.status_code == 422