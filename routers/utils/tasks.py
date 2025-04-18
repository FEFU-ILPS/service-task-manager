from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException
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
