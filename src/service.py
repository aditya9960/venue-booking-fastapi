from __future__ import annotations

from datetime import datetime, timedelta
from src.enums import EquipmentType
from src.db_service_interface import AbstractService
from src.solver import Solver


class BookingService:
    """
    service layer to finding availability & returning available
    """
    def __init__(self, repo: AbstractService, solver: Solver | None = None) -> None:
        # db obj representation
        self.repo = repo
        self.solver = solver or Solver()

    # find availability booking service
    def find_availability(
            self,
            earliest_start: datetime,
            duration_minutes: int,
            latest_end: datetime | None,
            requested_equipment: set[EquipmentType],
    ):
        print(self.repo.list_rooms())
        print(self.repo.list_equipment())
        print(self.repo.list_bookings())
        return self.solver.find_available_slot(
            earliest_start=earliest_start,
            duration=timedelta(minutes=duration_minutes),
            latest_end=latest_end,
            requested_equipment=requested_equipment,
            rooms=self.repo.list_rooms(),
            equipment=self.repo.list_equipment(),
            booked_slots=self.repo.list_bookings(),
        )

