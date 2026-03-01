import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from config.yaml_utils import read_yaml


params = read_yaml("config/config.yaml")
load_dotenv()  # Load environment variables from .env file

url: str = os.getenv("DEMO_SUPABASE_URL")
key: str = os.getenv("DEMO_SUPABASE_KEY")
supabase: Client = create_client(url, key)

def insert_image_generation_metadata_record(job_id: str, num_images: int, status: str):
    data = {
        "job_id": job_id,
        "job_created_at": datetime.now().isoformat(),
        "number_of_images": num_images,
        "job_status": status
    }
    response = supabase.table(params["metadata_database"]["supabase_table_name"]).insert(data).execute()
    return response

def get_image_generation_metadata_record(job_id: str):
    response = supabase.table(params["metadata_database"]["supabase_table_name"]).select("*").eq("job_id", job_id).execute()
    return response

def update_job_status(job_id: str, status: str, output_paths: list = None):
    
    data = {
        "job_status": status,
        "job_updated_at": datetime.now().isoformat()
    }
    
    # Add output paths if provided
    if output_paths is not None:
        data["output_paths"] = output_paths
    
    # Add completion timestamp if job is completed
    if status.upper() in ["COMPLETED", "FAILED"]:
        data["job_completed_at"] = datetime.now().isoformat()
    
    response = supabase.table(params["metadata_database"]["supabase_table_name"]).update(data).eq("job_id", job_id).execute()
    return response