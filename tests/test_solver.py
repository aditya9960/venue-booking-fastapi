from datetime import datetime, timedelta

from src.enums import EquipmentType
from src.solver import Solver


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def booking(
    booking_id: str,
    room_id: str,
    start: str,
    duration: int,
    equipment_ids: list[str] | None = None,
) -> dict:
    return {
        "booking_id": booking_id,
        "room_id": room_id,
        "start": start,
        "duration": duration,
        "equipment_ids": equipment_ids or [],
    }


def test_empty_system_returns_earliest_start() -> None:
    """
    With no bookings and no equipment requirements,
    the solver should return the earliest start and the smallest room.
    """
    solver = Solver()

    res = solver.find_available_slot(
        earliest_start=dt("2026-01-01T10:00:00Z"),
        duration=timedelta(minutes=60),
        latest_end=None,
        requested_equipment=set(),
        rooms=["room2", "room1"],
        equipment={},
        booked_slots=[],
    )

    assert res is not None
    room_id, start, equipment_ids = res
    assert room_id == "room1"
    assert start == dt("2026-01-01T10:00:00Z")
    assert equipment_ids == set()


def test_simple_room_conflict_pushes_start_time() -> None:
    """
    If the only room is booked at earliest_start,
    the solver should move to the end of the booking.
    """
    solver = Solver()

    res = solver.find_available_slot(
        earliest_start=dt("2026-01-01T10:00:00Z"),
        duration=timedelta(minutes=30),
        latest_end=None,
        requested_equipment=set(),
        rooms=["room1"],
        equipment={},
        booked_slots=[
            booking("b1", "room1", "2026-01-01T10:00:00Z", 60),
        ],
    )

    assert res is not None
    room_id, start, _ = res
    assert room_id == "room1"
    assert start == dt("2026-01-01T11:00:00Z")


def test_simple_equipment_selection() -> None:
    """
    When multiple equipment items of the same type exist,
    the solver should pick one that is free.
    """
    solver = Solver()

    res = solver.find_available_slot(
        earliest_start=dt("2026-01-01T10:00:00Z"),
        duration=timedelta(minutes=30),
        latest_end=None,
        requested_equipment={EquipmentType.PROJECTOR},
        rooms=["room1"],
        equipment={"projector": ["p1", "p2"]},
        booked_slots=[
            booking("b1", "roomX", "2026-01-01T10:00:00Z", 30, ["p1"]),
        ],
    )

    assert res is not None
    _, start, equipment_ids = res
    assert start == dt("2026-01-01T10:00:00Z")
    assert equipment_ids == {"p2"}


def test_no_solution_when_equipment_is_fully_booked() -> None:
    """
    If all equipment items of a requested type are booked for the whole window,
    the solver should return None.
    """
    solver = Solver()

    res = solver.find_available_slot(
        earliest_start=dt("2026-01-01T10:00:00Z"),
        duration=timedelta(minutes=30),
        latest_end=dt("2026-01-01T11:00:00Z"),
        requested_equipment={EquipmentType.MICROPHONE},
        rooms=["room1"],
        equipment={"microphone": ["m1"]},
        booked_slots=[
            booking("b1", "roomX", "2026-01-01T09:00:00Z", 180, ["m1"]),
        ],
    )

    assert res is None
