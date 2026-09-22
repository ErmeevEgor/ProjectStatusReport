from .rules import (
    calculate_progress,
    coefficient,
    inherit_parent_periods,
    normalize_status,
    page2_contractual_rows,
)
from .validation import validate_report

__version__ = "0.2.0"

__all__ = [
    "calculate_progress",
    "coefficient",
    "inherit_parent_periods",
    "normalize_status",
    "page2_contractual_rows",
    "validate_report",
]
