import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Column, Enum, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index

from .engine import BaseORM
from .types import Status


class Task(BaseORM):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(Status), nullable=False, default=Status.CREATED)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    text_id = Column(UUID(as_uuid=True), nullable=False)
    result = Column(TEXT, nullable=True, default=None)
    created_at = Column(TIMESTAMP, nullable=False, default=lambda _: datetime.now(tz=timezone.utc))
    completed_at = Column(TIMESTAMP, nullable=True, default=None)
    comment = Column(TEXT, nullable=True, default=None)

    __table_args__ = (
        Index("task_text_id_idx", text_id, postgresql_using="hash"),
        Index("task_user_id_idx", user_id, postgresql_using="hash"),
    )
