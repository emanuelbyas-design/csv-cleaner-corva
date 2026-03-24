import csv
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

MAX_ROWS = 1_048_000


@dataclass
class CleanResult:
    output_paths: list[str] = field(default_factory=list)
    total_rows: int = 0
    kept_rows: int = 0
    removed_rows: int = 0


class BaseCleaner:
    """Shared cleaning infrastructure. Subclasses override specific hooks."""

    provider_name: str = "Unknown"

    # Subclasses set these: 0-based column indices to check for -999.25
    bad_value_columns: list[int] = []

    def __init__(self, filepath: str, progress_cb: Optional[Callable[[float], None]] = None):
        self.filepath = filepath
        self._progress_cb = progress_cb
        self._original_header: list[str] = []

    def _report_progress(self, fraction: float):
        if self._progress_cb:
            self._progress_cb(min(fraction, 1.0))

    def _output_path(self, part: int | None = None) -> str:
        base, ext = os.path.splitext(self.filepath)
        suffix = f"_part{part}" if part is not None else ""
        return f"{base}_Corva_Formatted{suffix}{ext}"

    def read_csv(self) -> tuple[list[str], list[list[str]]]:
        """Read CSV preserving original header and all rows as string lists."""
        with open(self.filepath, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        self._original_header = header
        return header, rows

    def rename_header(self, header: list[str]) -> list[str]:
        """Rename header fields. Override in subclass if needed."""
        return header

    def fix_timestamp(self, row: list[str]) -> list[str]:
        """Reformat timestamp in a single row. Override in subclass if needed."""
        return row

    def fix_row_values(self, row: list[str]) -> list[str]:
        """Fix data values in a single row. Override if needed."""
        return row

    def is_bad_row(self, row: list[str]) -> bool:
        """Return True if the row should be deleted (-999.25 in key columns)."""
        for col_idx in self.bad_value_columns:
            if col_idx < len(row):
                if row[col_idx].strip() == "-999.25":
                    return True
        return False

    def write_csv(self, header: list[str], rows: list[list[str]], output_path: str):
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def clean(self) -> CleanResult:
        self._report_progress(0.0)

        header, rows = self.read_csv()
        total_rows = len(rows)
        self._report_progress(0.2)

        header = self.rename_header(header)
        self._report_progress(0.3)

        cleaned_rows = []
        for i, row in enumerate(rows):
            if self.is_bad_row(row):
                continue
            row = self.fix_timestamp(row)
            row = self.fix_row_values(row)
            cleaned_rows.append(row)

            if i % 10000 == 0:
                frac = 0.3 + 0.5 * (i / max(total_rows, 1))
                self._report_progress(frac)

        kept_rows = len(cleaned_rows)
        self._report_progress(0.8)

        output_paths: list[str] = []
        if kept_rows <= MAX_ROWS:
            path = self._output_path()
            self.write_csv(header, cleaned_rows, path)
            output_paths.append(path)
        else:
            part = 1
            for start in range(0, kept_rows, MAX_ROWS):
                chunk = cleaned_rows[start : start + MAX_ROWS]
                path = self._output_path(part=part)
                self.write_csv(header, chunk, path)
                output_paths.append(path)
                part += 1
                frac = 0.8 + 0.2 * (start + len(chunk)) / kept_rows
                self._report_progress(frac)

        self._report_progress(1.0)

        return CleanResult(
            output_paths=output_paths,
            total_rows=total_rows,
            kept_rows=kept_rows,
            removed_rows=total_rows - kept_rows,
        )
