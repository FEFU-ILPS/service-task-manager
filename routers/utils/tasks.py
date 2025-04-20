import asyncio
from datetime import datetime, timezone
from io import BytesIO
from typing import AsyncGenerator

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Task
from database.types import Status

from .preprocessing import preprocess_audio
from .transcribing import transcribe_audio


async def start_task(audio_file: BytesIO, task_obj: Task, db: AsyncSession):
    """Запускает в работу задачу на обработку аудиофайла, возвращая извлеченную
    из него фонетическую запись прочитанного текста. Функция также управляет
    статусом задачи.

    Args:
        audio_file (BytesIO): Поток байтов аудиофайала.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.
    """
    try:
        db.add(task_obj)
        task_obj.status = Status.STARTED
        await db.commit()

        preprocessed_audio_file = await preprocess_audio(audio_file, task_obj, db)
        text_transcription = await transcribe_audio(preprocessed_audio_file, task_obj, db)
        task_obj.status = Status.COMPLETED
        task_obj.result = text_transcription
        await db.commit()

    except HTTPException as e:
        task_obj.status = Status.FAILED
        task_obj.comment = e.detail

    except Exception:
        task_obj.status = Status.FAILED

    finally:
        task_obj.completed_at = datetime.now(tz=timezone.utc)
        await db.commit()


async def stream_task(
    task_obj: Task, db: AsyncSession, req: Request, on_update: bool = True
) -> AsyncGenerator[str, None]:
    """Функция создает обьект-генератор, позволяющий стримить состояние
    выполнения задачи в реальном времени.

    Args:
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.
        req (Request): Обьект запроса на сервер.
        on_update (bool, optional): Отправлять данные только при обновлении.
            Defaults to True.

    Yields:
        AsyncGenerator[str, None, Any]: Генератор строки состояния задачи.
    """
    last_status = Status.UNKNOWN
    db.add(task_obj)

    while True:
        if await req.is_disconnected():
            break

        current_status = task_obj.status

        if current_status != last_status or not on_update:
            last_status = current_status
            event_data = {
                "event": "status_updated" if on_update else "status_checked",
                "task_id": str(task_obj.id),
                "status": current_status.value,
                "retry": 15000,
            }
            yield str(event_data)

            if current_status in (Status.COMPLETED, Status.FAILED):
                break

        await db.refresh(task_obj)
        await asyncio.sleep(1)
