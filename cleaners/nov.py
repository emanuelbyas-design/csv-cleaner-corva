from datetime import datetime
from .base import BaseCleaner


class NOVCleaner(BaseCleaner):
    provider_name = "NOV"
    bad_value_columns = [1, 2]  # col B (Hole Depth), col C (Bit Position)

    def rename_header(self, header: list[str]) -> list[str]:
        if header[0] in ("Date Time", "DateTime"):
            header[0] = "Datetime"
        return header

    def fix_timestamp(self, row: list[str]) -> list[str]:
        val = row[0].strip()
        if not val:
            return row
        for fmt_in, fmt_out in [
            ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"),
            ("%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M:%S"),
            ("%m/%d/%y %H:%M", "%m/%d/%Y %H:%M:%S"),
            ("%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S"),
        ]:
            try:
                dt = datetime.strptime(val, fmt_in)
                row[0] = dt.strftime(fmt_out)
                break
            except ValueError:
                continue
        return row

    def fix_row_values(self, row: list[str]) -> list[str]:
        """Strip trailing zeros from numeric values (skip timestamp col 0)."""
        for i in range(1, len(row)):
            row[i] = _strip_trailing_zeros(row[i])
        return row


def _strip_trailing_zeros(val: str) -> str:
    val = val.strip()
    if not val:
        return val
    try:
        f = float(val)
    except ValueError:
        return val
    if f == int(f):
        return str(int(f))
    return val
