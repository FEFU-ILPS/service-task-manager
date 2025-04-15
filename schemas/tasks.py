from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from uuid import UUID
from database.types import Status


TaskID = Annotated[UUID, Field(description="Уникальный идентификатор")]
TaskUserID = Annotated[UUID, Field(description="Идентификатор пользователя")]
TaskTextID = Annotated[UUID, Field(description="Идентификатор текста")]
TaskStatus = Annotated[Status, Field(description="Статуст выполнения")]
TaskResult = Annotated[str, Field(description="Результат транскрибирования")]


class CreateTaskResponse(BaseModel):
    """Данные, отправляемые в ответ на создание задачи."""

    model_config = ConfigDict(from_attributes=True)

    id: TaskID


class TasksResponse(CreateTaskResponse):
    """Данные, отправляемые в ответ на получение задач."""

    user_id: TaskUserID
    status: TaskStatus


class DetailTaskResponse(CreateTaskResponse):
    """Данные, отправляемые в ответ на получение информации
    по конкретной задаче.
    """

    user_id: TaskUserID
    text_id: TaskTextID
    status: TaskStatus
    result: TaskResult
