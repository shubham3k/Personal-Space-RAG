"""Small date extraction helpers."""

import re
from datetime import datetime


DATE_PATTERNS = [
    r"(?P<date>\d{4}-\d{2}-\d{2})",
    r"(?P<date>\d{4}_\d{2}_\d{2})",
    r"(?P<date>\d{8})",
]


def _normalize(value: str) -> str | None:
    for fmt in ("%Y-%m-%d", "%Y_%m_%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_date_from_filename(name: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, name)
        if match:
            return _normalize(match.group("date"))
    return None


def extract_date_from_text(text: str) -> str | None:
    return extract_date_from_filename(text)
