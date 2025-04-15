import uuid
from datetime import datetime, timezone

from sqlalchemy import DATETIME, Column, Enum, TEXT
from sqlalchemy.dialects.postgresql import UUID

from .engine import BaseORM
from .types import Status


class Task(BaseORM):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(Status), nullable=False, default=Status.CREATED)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    text_id = Column(UUID(as_uuid=True), nullable=False)
    result = Column(TEXT, nullable=True, default=None)
    created_at = Column(DATETIME, nullable=False, default=lambda _: datetime.now(tz=timezone.utc))
    completed_at = Column(DATETIME, nullable=True, default=None)
