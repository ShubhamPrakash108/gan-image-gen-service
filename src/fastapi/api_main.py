from pydantic import BaseModel, Field
from src.core.job_enum import JobStatus
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import json
import os
from uuid import uuid4
from src.queue.publisher import publish_image_job
from src.database_operation.metadata_db import insert_image_generation_metadata_record, get_image_generation_metadata_record
from config.yaml_utils import read_yaml

app = FastAPI()

params = read_yaml("config/config.yaml")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

class ImageGenerationRequest(BaseModel):
    num_images: int = Field(gt=0, le=5)
    status: str = JobStatus.PENDING.value

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus

class JobDetailsResponse(BaseModel):
    job_id: str
    status: JobStatus
    num_images: Optional[int] = None
    output_paths: Optional[List[Optional[str]]] = None

@app.post("/generate/image", response_model=JobResponse, status_code=202) # 202 Accepted
async def create_image_generation_job(request: ImageGenerationRequest):
    job_id = str(uuid4())

    # 1. Save job to DB (status = PENDING)
    response = insert_image_generation_metadata_record(job_id, request.num_images, request.status)
    print(f"DB Insert Response: {response}")
    # 2. Publish job_id + params to RabbitMQ
    publish_image_job(job_id, request.num_images)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
    )

@app.get("/job/{job_id}", response_model=JobResponse)
async def get_image_generation_job_status(job_id: str):

    response = get_image_generation_metadata_record(job_id)

    return JobResponse(
        job_id=job_id,
        status=response.data[0]["job_status"] 
    )

@app.get("/job/{job_id}/details", response_model=JobDetailsResponse)
async def get_image_generation_job_details(job_id: str):
    response = get_image_generation_metadata_record(job_id)
    if not response.data:
        raise HTTPException(status_code=404, detail="Job not found")

    record = response.data[0]
    output_paths = record.get("output_paths")
    if isinstance(output_paths, str):
        try:
            output_paths = json.loads(output_paths)
        except json.JSONDecodeError:
            output_paths = [output_paths]

    return JobDetailsResponse(
        job_id=job_id,
        status=record["job_status"],
        num_images=record.get("number_of_images"),
        output_paths=output_paths,
    )
