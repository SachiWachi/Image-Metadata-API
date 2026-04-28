# main.py
import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS, IFD

# Import our database configuration and models
from database import engine, SessionLocal, Base
import models

# Create the database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Image Metadata API",
    description="A microservice for extracting and logging image telemetry data.",
    version="1.0.0"
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to parse raw EXIF data into a clean JSON-serializable dictionary
def parse_exif(image: Image.Image) -> dict:
    exif_raw = image.getexif()
    if not exif_raw:
        return None
        
    parsed_exif = {}
    
    # 1. Parse the top-level standard EXIF tags
    for tag_id, value in exif_raw.items():
        tag_name = TAGS.get(tag_id, tag_id)
        if isinstance(value, bytes):
            continue
        parsed_exif[str(tag_name)] = str(value)
        
    # 2. explicitly follow the pointer to the GPS IFD (Image File Directory)
    try:
        # IFD.GPSInfo is the standardized enum for tag 34853
        gps_info_raw = exif_raw.get_ifd(IFD.GPSInfo)
        
        if gps_info_raw:
            parsed_gps = {}
            for gps_tag_id, gps_value in gps_info_raw.items():
                # Translate the GPS tag ID using GPSTAGS instead of standard TAGS
                gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                
                if isinstance(gps_value, bytes):
                    continue
                    
                # Convert the complex fractional tuples into strings for JSON safety
                parsed_gps[str(gps_tag_name)] = str(gps_value)
                
            # Nest the decoded GPS dictionary inside the main EXIF payload
            parsed_exif["GPSInfo_Decoded"] = parsed_gps
            
    except KeyError:
        # Fails silently if the image simply doesn't have a GPS block
        pass
        
    return parsed_exif

@app.post("/upload-image/")
async def extract_image_metadata(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Accepts an image file upload, reads it into memory, extracts 
    structural metadata and EXIF telemetry, and logs the record to PostgreSQL.
    """
    contents = await file.read()
    file_size_kb = round(len(contents) / 1024, 2)

    try:
        image = Image.open(io.BytesIO(contents))

        # Parse the EXIF data using our helper function
        clean_exif_dict = parse_exif(image)

        # 1. Prepare the data for the API response
        metadata_response = {
            "filename": file.filename,
            "format": image.format,
            "width_px": image.width,
            "height_px": image.height,
            "color_mode": image.mode,
            "file_size_kb": file_size_kb,
            "exif_data": clean_exif_dict
        }

        # 2. Write the record to the PostgreSQL database
        db_record = models.ImageMetadata(
            filename=file.filename,
            format=image.format,
            width_px=image.width,
            height_px=image.height,
            color_mode=image.mode,
            file_size_kb=file_size_kb,
            exif_data=clean_exif_dict # SQLAlchemy handles the dict-to-JSONB conversion
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        metadata_response["db_id"] = db_record.id

        return {"status": "success", "data": metadata_response}

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a valid image (JPEG, PNG, etc.)."
        )
    finally:
        await file.close()