# main.py
from fastapi import FastAPI

# Initialize the FastAPI application with metadata for the auto-generated documentation
app = FastAPI(
    title="Image Metadata API",
    description="A microservice for extracting and logging image telemetry data.",
    version="1.0.0"
)

@app.get("/")
async def root():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "Image Metadata API is online."}