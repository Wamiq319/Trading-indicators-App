def interval_to_seconds(interval: str) -> int:
    if interval.endswith("d"):
        return int(interval[:-1]) * 86400
    elif interval.endswith("h"):
        return int(interval[:-1]) * 3600
    elif interval.endswith("m"):
        return int(interval[:-1]) * 60
    else:
        raise ValueError("Invalid interval format. Use '1d', '1h', or '1m'.")
