from .base import BaseCleaner


class PasonCleaner(BaseCleaner):
    provider_name = "Pason"
    bad_value_columns = [2, 3]  # col C (Hole Depth), col D (Bit Depth)
