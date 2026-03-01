import pika
import json
import sys
from src.inference.gan_model_inference_image import job_generate_image
from src.inference.gan_model_inference_gif import job_generate_gif
from src.database_operation.metadata_db import update_job_status
from src.core.job_enum import JobStatus
from config.yaml_utils import read_yaml
from dotenv import load_dotenv
import os
load_dotenv()

config = read_yaml("config/config.yaml")

def get_rabbitmq_connection():
    params = pika.URLParameters(os.getenv("RABBITMQ_HOST"))
    return pika.BlockingConnection(params)

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        job_id = message['job_id']
        
        print(f"Processing job: {job_id}")
        
        # Update status to PROCESSING
        update_job_status(job_id, JobStatus.PROCESSING.value)
        
        paths = job_generate_image(job_id, message['num_images'])
        print(f"Generated image paths: {paths}")
        update_job_status(job_id, JobStatus.COMPLETED.value, paths)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Job {job_id} completed successfully")
        
    except Exception as e:
        print(f"Error processing job: {e}")
        # Update status to FAILED
        update_job_status(message['job_id'], JobStatus.FAILED.value)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_worker():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue=config['rabbitmq_service']['image_generation_queue'], durable=True)
    channel.basic_qos(prefetch_count=1)  # Process one job at a time
    
    channel.basic_consume(
        queue=config['rabbitmq_service']['image_generation_queue'],
        on_message_callback=callback
    )
    
    print('Worker waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()