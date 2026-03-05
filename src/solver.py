from datetime import datetime, timedelta

from src.enums import EquipmentType


def _to_datetime(value: datetime | str) -> datetime:
    """helper function"""
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

class Solver:
    @staticmethod
    def check_overlaps(start_int1: datetime, end_int1: datetime, start_int2: datetime, end_int2: datetime) -> bool:
        # half-open intervals : if both true then overlap else not
        return start_int1 < end_int2 and start_int2 < end_int1

    def find_available_slot(
        self,
        earliest_start: datetime,
        duration: timedelta,
        latest_end: datetime | None,
        requested_equipment: set[EquipmentType],
        rooms: list[str],
        equipment: dict[str, list[str]],
        booked_slots: list[dict],
    ) -> tuple[str, datetime, set[str]] | None:
        # NOTE: please don't change the signature of this method
        # as it is used by the automated tests
        # if no rooms are available, None returned
        if not rooms:
            return None
        # sorting for lex order
        rooms = sorted(rooms)

        # define earliest start
        latest_start = None
        if latest_end is not None:
            latest_start = latest_end - duration
            if latest_start < earliest_start:
                # not available
                return None

        # parsing bookings
        parsed = []

        for slot in booked_slots:
            slot_start = _to_datetime(slot["start"])
            slot_end = slot_start + timedelta(minutes=slot["duration"])
            parsed.append(
                (slot["room_id"], slot_start, slot_end, set(slot.get("equipment_ids", [])))
            )

        # candidate times = earliest_start + all booking boundaries
        candidate_times: set[datetime] = {earliest_start}
        for _, slot_start, slot_end, _ in parsed:
            if slot_start >= earliest_start:
                candidate_times.add(slot_start)
            if slot_end >= earliest_start:
                candidate_times.add(slot_end)

        for start_time in sorted(candidate_times):
            # skip time which is not possible
            if start_time < earliest_start:
                continue
            # stop for possible time slot
            if latest_start is not None and start_time > latest_start:
                break

            end_time = start_time + duration

            # check rooms in lex order
            for room in rooms:
                # check room free
                if any(
                        room_prased == room and Solver.check_overlaps(start_time, end_time, slot_start_parsed,
                                                                      slot_end_parsed)
                        for room_prased, slot_start_parsed, slot_end_parsed, _ in parsed
                ):
                    continue

                chosen_equipment: set[str] = set()

                booking_conditions_flag = True

                for eq_type in sorted(requested_equipment, key=lambda x: x.value):  #sorted for lex order
                    equip_ids = sorted(equipment.get(eq_type.value, []))
                    free_id = None

                    for eid in equip_ids:
                        if not any(
                                eid in eq_ids_parsed and Solver.check_overlaps(start_time, end_time, slot_start_parsed,
                                                                               slot_end_parsed)
                                for _, slot_start_parsed, slot_end_parsed, eq_ids_parsed in parsed
                        ):
                            free_id = eid
                            break

                    if free_id is None:
                        booking_conditions_flag = False
                        break

                    chosen_equipment.add(free_id)

                if booking_conditions_flag:
                    return room, start_time, chosen_equipment
        return None
