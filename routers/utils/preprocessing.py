import asyncio
from io import BytesIO

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Task
from database.types import Status


async def preprocess_audio(audio_file: BytesIO, task_obj: Task, db: AsyncSession) -> BytesIO:
    """Функция передает поток байтов аудиофайла на сервис предобработки,
    параллельно меняя статус задачи.

    Функция при помощи сервиса предобработки возвращает поток байтов
    аудиофайла с изменеными значениями и свойств аудио: Частота дискретизации, усиление и т.п.

    Args:
        audio_file (BytesIO): Поток байтов аудиофайала.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        BytesIO: Поток байтов обработанного аудиофайла.
    """
    task_obj.status = Status.PREPROCESSING
    await db.commit()

    async with httpx.AsyncClient() as client:
        try:
            # TODO: Написать логику запроса на предобработку
            await asyncio.sleep(15)  # Имитация обработки

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json().get("detail", "Unknown error"),
            )

    return audio_file
