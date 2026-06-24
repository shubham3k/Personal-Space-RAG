"""Rate-limit math helpers."""


def per_minute_to_per_second(value: int) -> float:
    return value / 60.0
