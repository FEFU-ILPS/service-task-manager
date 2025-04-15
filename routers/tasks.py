from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter()


@router.get("/", summary="Получить список задач")
async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получает список всех задач, когда либо созданных в системе ILPS."""


@router.get("/{uuid}", summary="Получить актуальную информацию о задаче")
async def get_task(
    uuid: Annotated[UUID, Path(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получает текущую информацию по UUID указаной задачи.
    Возвращает полную информацию о задача.
    """


@router.post("/", summary="Создать задачу на обработку аудио файла")
async def create_task(
    file: UploadFile,
    background: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Создаёт задачу на предобработку и транскрибирование аудиофайла.
    Возвращает UUID созданой задачи с ответом 200, выполняя её в фоне.
    """
