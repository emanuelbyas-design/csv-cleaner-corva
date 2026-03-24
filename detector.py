import csv
from typing import Optional


PROVIDERS = ("NOV", "Rigcloud", "Pason")


def detect_provider(filepath: str) -> Optional[str]:
    """Auto-detect EDR provider by inspecting the first header cell of the CSV."""
    try:
        with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return None

            first_col = header[0].strip()

            if first_col == "Date Time":
                return "NOV"
            if first_col == "Time":
                return "Rigcloud"
            if first_col == "Datetime":
                second = header[1].strip() if len(header) > 1 else ""
                if second.startswith("Total Depth") or second.startswith("Pit Volume"):
                    return "Rigcloud"
                return "NOV"
            if first_col == "YYYY/MM/DD":
                return "Pason"
            if first_col == "DateTime":
                return "NOV"

    except Exception:
        return None

    return None
