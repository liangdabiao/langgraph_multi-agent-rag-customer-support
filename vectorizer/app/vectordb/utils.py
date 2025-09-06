from datetime import datetime, timezone

def get_timestamp_in_utc(datetime_iso: str) -> int:
    if not datetime_iso:
        return 0

    is_utc_format = datetime_iso.endswith('Z')

    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.strptime(datetime_iso, "%Y-%m-%dT%H:%M:%S.%f")

    if is_utc_format:
        return int(dt.timestamp() * 1_000)
    else:
        dt_utc = dt.astimezone(timezone.utc)
        return int(dt_utc.timestamp() * 1_000)

def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
