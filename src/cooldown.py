from datetime import datetime, timedelta
from config import COOLDOWN_MINUTES

active_incidents = {}

def is_in_cooldown(service, incident_type):

    key = f"{service}:{incident_type}"

    if key not in active_incidents:
        return False

    last = active_incidents[key]

    if datetime.utcnow() - last > timedelta(minutes=COOLDOWN_MINUTES):
        return False

    return True


def register_incident(service, incident_type):
    key = f"{service}:{incident_type}"
    active_incidents[key] = datetime.utcnow()
