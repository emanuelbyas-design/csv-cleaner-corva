from .base import BaseCleaner


class RigcloudCleaner(BaseCleaner):
    provider_name = "Rigcloud"
    bad_value_columns = [1, 15]  # col B (Total Depth), col P (Depth - Bit)

    def rename_header(self, header: list[str]) -> list[str]:
        if header[0] == "Time":
            header[0] = "Datetime"
        return header
