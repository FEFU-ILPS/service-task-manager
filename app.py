from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import disconnect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_startup

    yield

    # on_shutdown
    await disconnect_db()


service = FastAPI(lifespan=lifespan)
