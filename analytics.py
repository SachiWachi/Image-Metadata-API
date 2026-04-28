# analytics.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Securely connect to the database
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def run_analysis():
    print("Fetching data from PostgreSQL...")

    # 2. Extract: Read the SQL table directly into a Pandas DataFrame
    query = "SELECT * FROM image_metadata;"
    df = pd.read_sql(query, engine)

    if df.empty:
        print("The database is empty. Please upload some images via the API first!")
        return

    # 3. Transform: Parse the JSONB column to extract specific EXIF data
    # We will extract the camera 'Make' and 'Model' if they exist in the JSON
    print("Cleaning and transforming JSONB EXIF data...")

    def extract_camera_model(exif_dict):
        if isinstance(exif_dict, dict):
            make = exif_dict.get("Make", "Unknown")
            model = exif_dict.get("Model", "Unknown")
            if make != "Unknown" and model != "Unknown":
                return f"{make} {model}".strip()
        return "No EXIF / Unknown"

    # Apply the extraction function to create a new column
    df["camera_model"] = df["exif_data"].apply(extract_camera_model)

    # 4. Analyze: Group the data to see the most popular cameras
    camera_counts = df["camera_model"].value_counts()
    print("\n--- Top Camera Models ---")
    print(camera_counts)

    # 5. Visualize: Generate a bar chart
    plt.figure(figsize=(10, 6))
    camera_counts.plot(kind="bar", color="steelblue", edgecolor="black")

    plt.title("Distribution of Uploaded Images by Camera Model", fontsize=14)
    plt.xlabel("Camera Model", fontsize=12)
    plt.ylabel("Number of Images", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the plot as an image instead of just showing it
    output_file = "camera_distribution_chart.png"
    plt.savefig(output_file)
    print(f"\nSuccess! Chart saved as {output_file}")

if __name__ == "__main__":
    run_analysis()