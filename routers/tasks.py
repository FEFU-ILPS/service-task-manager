from io import BytesIO
from typing import Annotated, List
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Task
from schemas.tasks import (
    CreateTaskResponse,
    DetailTaskRequest,
    DetailTaskResponse,
    TasksRequest,
    TasksResponse,
)

from .utils.tasks import start_task

router = APIRouter()


@router.post("/transcribe", summary="Создать задачу на обработку аудио файла")
async def create_task(
    file: Annotated[UploadFile, File(...)],
    user_id: Annotated[UUID, Form(...)],
    text_id: Annotated[UUID, Form(...)],
    background: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateTaskResponse:
    """Создаёт задачу на предобработку и транскрибирование аудиофайла.
    Возвращает UUID созданой задачи с ответом 200, выполняя её в фоне.
    """
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file extension. Only .wav files are accepted.",
        )

    if file.content_type not in ["audio/wav", "audio/x-wav", "application/octet-stream", None]:
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only audio/wav MIME is accepted.",
        )

    created_task = Task(
        user_id=user_id,
        text_id=text_id,
    )

    db.add(created_task)
    await db.commit()
    await db.refresh(created_task)

    audio_file = BytesIO(await file.read())
    background.add_task(start_task, audio_file, created_task, db)

    return CreateTaskResponse.model_validate(created_task)


# * GET был заменен на POST ради Body
@router.post("/", summary="Получить список задач")
async def get_tasks(
    data: Annotated[TasksRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[TasksResponse]:
    """Получает список всех задач, когда либо созданных в системе ILPS."""

    stmt = select(Task).where(Task.user_id == data.user_id)
    tasks = await db.execute(stmt)
    tasks = tasks.scalars().all()

    return [TasksResponse.model_validate(task) for task in tasks]


# * GET был заменен на POST ради Body
@router.post("/{uuid}", summary="Получить актуальную информацию о задаче")
async def get_task(
    uuid: Annotated[UUID, Path(...)],
    data: Annotated[DetailTaskRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DetailTaskResponse:
    """Получает текущую информацию по UUID указаной задачи.
    Возвращает полную информацию о задача.
    """

    stmt = select(Task).where((Task.id == uuid) & (Task.user_id == data.user_id))
    task = await db.execute(stmt)
    task = task.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return DetailTaskResponse.model_validate(task)
