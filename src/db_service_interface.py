from __future__ import annotations
from typing import Protocol


class Booking(dict):
    """
    just for simply alias as dict for booking
    """
    pass

class AbstractService(Protocol):
    """
    absctracions for service interface for loose couple
    """
    # defining Rooms operations for db
    def list_rooms(self) -> list[str]: ...
    def add_room(self, room_id: str) -> None: ...
    def remove_room(self, room_id: str) -> None: ...

    # defining Equipment operations for db
    def list_equipment(self) -> dict[str, list[str]]: ...
    def add_equipment(self, eq_type: str, eq_id: str) -> None: ...
    def remove_equipment(self, eq_id: str) -> None: ...

    # defining Bookings operations
    def list_bookings(self) -> list[Booking]: ...
    def add_booking(self, booking: Booking) -> None: ...
    def delete_booking(self, booking_id: str) -> None: ...


