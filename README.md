# Smart Image Metadata API & Analytics Pipeline

An end-to-end data engineering and analytics pipeline built with Python. This microservice asynchronously processes image uploads, extracts complex EXIF telemetry, persists the data into a normalized PostgreSQL database, and provides automated visual analytics.

## 🏗️ Architecture & Tech Stack

- **Backend Framework:** FastAPI, Uvicorn (Asynchronous REST API)
- **Data Processing:** Pillow (PIL), Pandas, Matplotlib
- **Database & ORM:** PostgreSQL, SQLAlchemy
- **Data Structures:** Strict normalization (3NF) paired with `JSONB` for semi-structured EXIF telemetry.
- **Environment Management:** `python-dotenv`

## 🔄 The Data Lifecycle (ETL Pipeline)

This project demonstrates a complete data lifecycle from extraction to business insight:

1. **Extract:** The FastAPI endpoint (`POST /upload-image/`) asynchronously receives raw binary image files over HTTP.
2. **Transform:** The application processes the image in memory, extracting standard dimensions and decoding complex EXIF pointer data into a structured dictionary.
3. **Load:** SQLAlchemy maps the structured data and commits it to a PostgreSQL database, utilizing the `JSONB` data type to safely store unpredictable EXIF payloads without breaking schema normalization.
4. **Analyze:** A standalone Python script utilizes **Pandas** to query the SQL database, aggregate camera models from the nested JSONB data, and generate visual distribution metrics via **Matplotlib**.

## 🚀 Features

- **In-Memory Processing:** Images are parsed dynamically without being written to the local disk, optimizing I/O operations.
- **Automated API Documentation:** Interactive Swagger UI is generated natively via OpenAPI standards.
- **Secure Configuration:** Environment variables (`.env`) are strictly used for database credentials and secure routing.
- **Error Handling:** Robust exception handling for invalid file types and malformed telemetry data.

## 🛠️ Local Setup & Installation

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (Local Server or Cloud Instance)

### 2. Database Initialization
Create an empty database in your PostgreSQL server:
```sql
CREATE DATABASE image_metadata_db;
```

### 3. Clone & Environment Setup
```bash
git clone <your-repository-url>
cd image-metadata-api

# Initialize and activate the virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory and add your PostgreSQL connection string:
```text
DATABASE_URL=postgresql://username:password@localhost:5432/image_metadata_db
```

### 5. Run the API
Start the FastAPI server. SQLAlchemy will automatically generate the required database tables on boot.
```bash
uvicorn main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to access the interactive Swagger UI and upload test images.

### 6. Run the Analytics
Once the database is populated with sample images, execute the analytics script to generate the distribution chart:
```bash
python analytics.py
```