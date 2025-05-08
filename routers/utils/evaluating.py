from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from configs import configs
from database.models import Task
from database.types import Status


async def evaluate_transcription(
    transcription: str, task_obj: Task, db: AsyncSession
) -> dict[str, Any]:
    """Функция передает результирующую транскрипцию речи из аудиофайла на сервис отчетов,
    параллельно меняя статус задачи.

    Args:
        transcription (str): Транскрипция, извлеченная из текста.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        dict[str, Any]: Отчет по произношению.
    """
    task_obj.status = Status.EVALUATING
    await db.commit()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{configs.services.feedback.URL}/",
                json={
                    "text_id": str(task_obj.text_id),
                    "actual_result": transcription,
                },
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json().get("detail", "Unknown error"),
            )
