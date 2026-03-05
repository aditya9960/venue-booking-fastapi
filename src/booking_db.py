from __future__ import annotations
from collections import defaultdict
from src.db_service_interface import Booking


class BookingMemory:
    """
    class for actual db memory ops
    """
    def __init__(self):
        """
        initialize private vars for rooms, equipments & bookings
        """
        self._rooms: set[str] = set()  # for unique names
        self._equipment: dict[str, set[str]] = defaultdict(set)
        self._bookings: dict[str, Booking] = {}

    # for actual Rooms operations defined in db service interface
    def list_rooms(self) -> list[str]:
        return sorted(self._rooms)  # sorting for lex approch

    def add_room(self, room_id: str) -> None:
        # unique validation is added at route level
        self._rooms.add(room_id)

    def remove_room(self, room_id: str) -> None:
        self._rooms.discard(room_id)

    def room_exists(self, room_id: str) -> bool:
        # for future to remove this from routes
        pass

    # for actual Equipment operations defined in db service interface
    def list_equipment(self) -> dict[str, list[str]]:
        return {k: sorted(v) for k, v in self._equipment.items()}  # sorting for lex approch

    def add_equipment(self, eq_type: str, eq_id: str) -> None:
        # unique validation is added at route level
        self._equipment[eq_type].add(eq_id)

    def remove_equipment(self, eq_id: str) -> None:
        for ids in self._equipment.values():
            ids.discard(eq_id)

    # for actual Bookings operations defined in db service interface
    def list_bookings(self) -> list[Booking]:
        return list(self._bookings.values())

    def add_booking(self, booking: Booking) -> None:
        # unique validation is added at route level
        self._bookings[booking["booking_id"]] = booking

    def delete_booking(self, booking_id: str) -> None:
        self._bookings.pop(booking_id, None)  # .pop for avoiding error

