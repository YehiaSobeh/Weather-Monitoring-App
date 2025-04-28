from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.main import api_router
from redis_client import r as redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await redis_client.init()

    # Yield control back to FastAPI
    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok"}