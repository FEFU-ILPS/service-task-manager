import asyncio
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Task
from database.types import Status


async def transcribe_audio(audio_file: BytesIO, task_obj: Task, db: AsyncSession) -> str:
    """Функция передает поток байтов (файл) на сервис транскрибирования,
    параллельно меняя статус задачи.

    Функция при помощи сервиса транскрибирования возвращает строку,
    которая является фонетической записью прочитанного текста.

    Args:
        audio_file (BytesIO): Поток байтов аудиофайала.
        task_obj (Task): Обьект ORM задачи.
        db (AsyncSession): Обьект сессии базы данных.

    Returns:
        str: Фонетическая запись текста.
    """
    task_obj.status = Status.TRANSCRIBING
    await db.commit()

    # TODO: Написать логику запроса на транскрибирование
    await asyncio.sleep(15)  # Имитация обработки

    return "aaaaa"
