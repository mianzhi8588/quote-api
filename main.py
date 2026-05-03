from contextlib import asynccontextmanager

from fastapi import FastAPI
from quote_router import router as quote_router
from quote_storage import init_quote_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_quote_storage()
    yield


app = FastAPI(
    title="Quote Option Reader API",
    description="Read and validate packaging quote options, calculate packaging price, and store quote price results.",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(quote_router)


@app.get("/")
def read_root():
    return {
        "message": "Quote Option Reader API is running"
    }