from pydantic import BaseModel, model_validator
from src.enums import EquipmentType
from datetime import datetime
from typing import List, Optional, Set


class RoomCreate(BaseModel):
    """room req schema"""
    room_id: str


class EquipmentCreate(BaseModel):
    """equip req schema"""
    equipment_id: str
    equipment_type: EquipmentType


class BookingCreate(BaseModel):
    """booking req schema"""
    booking_id: str
    room_id: str
    start: datetime
    duration: int
    equipment_ids: List[str] = []


class AvailabilityRequest(BaseModel):
    """ availability req schema"""
    earliest_start: datetime
    duration: int
    latest_end: Optional[datetime] = None
    requested_equipment: Set[EquipmentType] = set()

