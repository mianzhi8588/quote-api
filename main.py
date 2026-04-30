from fastapi import FastAPI
from quote_router import router as quote_router


app = FastAPI(
    title="Quote Option Reader API",
    description="Read and validate packaging quote options. This version only parses input and does not calculate price.",
    version="1.0.0",
)


app.include_router(quote_router)


@app.get("/")
def read_root():
    return {
        "message": "Quote Option Reader API is running"
    }