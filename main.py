# main.py
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError

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

@app.post("/upload-image/")
async def extract_image_metadata(file: UploadFile = File(...)):
    """
    Accepts an image file upload, reads it into memory, and extracts 
    structural metadata (dimensions, format, file size).
    """
    # 1. Read the file asynchronously into memory
    contents = await file.read()
    file_size_kb = round(len(contents) / 1024, 2) # Convert bytes to kilobytes and round to 2 decimal places

    # 2. Process the image using Pillow
    try:
        # io.BytesIO treats the byte string like a file object
        image = Image.open(io.BytesIO(contents))

        # Extract standard metadata
        metadata = {
            "filename": file.filename,
            "format": image.format,
            "width_px": image.width,
            "height_px": image.height,
            "color_mode": image.mode,
            "file_size_kb": file_size_kb
        }

        # Extract EXIF data if it exists (mostly present in JPEGs)
        exif_data = image.getexif()
        if exif_data:
            # Just log that EXIF is present for now, parsing it completely requires mapping tags
            metadata["has_exif"] = True
        else:
            metadata["has_exif"] = False

        return {"status": "success", "data": metadata}

    except UnidentifiedImageError:
        # Handle the case where the uploaded file is not a valid image
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a valid image (JPEG, PNG, etc.)."
        )
    finally:
        # Free up memory by closing the uploaded file
        await file.close()