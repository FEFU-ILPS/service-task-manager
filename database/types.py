from enum import Enum


class Status(Enum):
    """Перечисление возможных значений статусов задачи."""

    CREATED = 0
    STARTED = 1
    PREPROCESSING = 2
    TRANSCRIBING = 3
    COMPLETED = 4
    FAILED = 5
