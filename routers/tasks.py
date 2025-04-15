from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models import Task
from schemas.tasks import CreateTaskResponse, DetailTaskResponse, TasksResponse

from .utils.tasks import spawn_task
from io import BytesIO

router = APIRouter()


@router.get("/", summary="Получить список задач")
async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[TasksResponse]:
    """Получает список всех задач, когда либо созданных в системе ILPS."""

    stmt = select(Task)
    tasks = await db.execute(stmt)
    tasks = tasks.scalars().all()

    return [TasksResponse.model_validate(**task) for task in tasks]


@router.get("/{uuid}", summary="Получить актуальную информацию о задаче")
async def get_task(
    uuid: Annotated[UUID, Path(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DetailTaskResponse:
    """Получает текущую информацию по UUID указаной задачи.
    Возвращает полную информацию о задача.
    """

    stmt = select(Task).where(Task.id == uuid)
    task = await db.execute(stmt)
    task = task.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return DetailTaskResponse.model_validate(task)


@router.post("/", summary="Создать задачу на обработку аудио файла")
async def create_task(
    file: UploadFile,
    background: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateTaskResponse:
    """Создаёт задачу на предобработку и транскрибирование аудиофайла.
    Возвращает UUID созданой задачи с ответом 200, выполняя её в фоне.
    """
    created_task = Task(
        user_id=None,
        text_id=None,
    )

    db.add(created_task)
    await db.commit()
    await db.refresh(created_task)

    audio_file = BytesIO(await file.read())
    background.add_task(spawn_task, audio_file, created_task, db)

    return CreateTaskResponse.model_validate(created_task)
