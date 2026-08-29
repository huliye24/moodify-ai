"""Runtime compatibility helpers for the package's declared Python range."""

try:
    from enum import StrEnum
except ImportError:  # Python 3.10
    from enum import Enum

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return self.value

