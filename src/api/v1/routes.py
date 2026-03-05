from fastapi import APIRouter, HTTPException, status
from src.schemas import RoomCreate, EquipmentCreate, BookingCreate, AvailabilityRequest
from src.booking_db import BookingMemory
from src.service import BookingService

router = APIRouter()
booking_db = BookingMemory()
service = BookingService(booking_db)

# TODO logger

@router.get("/rooms")
def list_rooms():
    """ get list of all rooms"""
    return booking_db.list_rooms()


@router.post("/rooms")
def add_room(payload: RoomCreate):
    """ add a room in rooms list"""
    try:
        # alternative: do in booking_db.py/ create booking_db in same file & import here
        if payload.room_id in booking_db._rooms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room already exists"
            )
        booking_db.add_room(payload.room_id)
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Please contact admin"}
    return {"status": "success", "msg": "Room Created."}


@router.delete("/rooms/{room_id}")
def delete_room(room_id: str):
    """ delete a room from rooms """
    try:
        booking_db.remove_room(room_id)
    except Exception as e:
        # print(e)
        return {"status": "failed", "msg": "Room delete failed"}
    return {"status": "success", "msg": "Room Deleted."}


@router.get("/equipment")
def list_equipment():
    """ get list of all equipment"""
    return booking_db.list_equipment()


@router.post("/equipment")
def add_equipment(payload: EquipmentCreate):
    """ add an equipment"""
    try:
        # equip_id are unique validation
        if any(payload.equipment_id in equipment_types for equipment_types in booking_db._equipment.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment already exists"
            )
        booking_db.add_equipment(payload.equipment_type.value, payload.equipment_id)
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Equipment adding failed"}
    return {"status": "success", "msg": "Equipment added."}



@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: str):
    """ remove the equipment"""
    try:
        booking_db.remove_equipment(equipment_id)
    except Exception as e:
        # print(e)
        return {"status": "failed", "msg": "Equipment delete failed"}
    return {"status": "success", "msg": "Equipment deleted."}


# -------------------- Bookings --------------------

@router.get("/bookings")
def list_bookings():
    """ get list of bookings """
    return booking_db.list_bookings()


@router.post("/bookings")
def create_booking(payload: BookingCreate):
    """ create a booking """
    # validations later move from here
    if payload.booking_id in booking_db._bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking id already exists"
        )
    if payload.room_id not in booking_db._rooms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room id '{payload.room_id}' does not exist"
        )

    for eq_id in payload.equipment_ids:
        if not any(eq_id in equipment_set for equipment_set in booking_db._equipment.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Equipment id '{eq_id}' does not exist"
            )
    try:
        booking_db.add_booking(payload.model_dump())
    except Exception as e:
        # print(e)
        return {"status": "failed", "msg": "Booking failed"}
    return {"status": "success", "msg": "Booking created."}


@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: str):
    """ delete the booking"""
    try:
        booking_db.delete_booking(booking_id)
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Booking delete failed"}
    return {"status": "success", "msg": "Booking Deleted."}

@router.post("/availability")
def availability(req: AvailabilityRequest):
    try:
        res = service.find_availability(
            earliest_start=req.earliest_start,
            duration_minutes=req.duration,
            latest_end=req.latest_end,
            requested_equipment=req.requested_equipment,
        )
    except Exception as e:
        print(e)
        return {"status": "failed", "msg": "Please contact admin"}

    if res is None:
        return {"available": False}

    room, start, equipment_ids = res

    return {
        "available": True,
        "room_id": room,
        "start": start,
        "equipment_ids": sorted(list(equipment_ids)),
    }