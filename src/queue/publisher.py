import pika
import json
from config.yaml_utils import read_yaml
from dotenv import load_dotenv
import os
load_dotenv()

config = read_yaml("config/config.yaml")
url = os.getenv("RABBITMQ_HOST")

def get_rabbitmq_connection():
    params = pika.URLParameters(url)
    return pika.BlockingConnection(params)

def publish_image_job(job_id: str, num_images: int):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare queue (idempotent)
    channel.queue_declare(queue=config['rabbitmq_service']['image_generation_queue'], durable=True)
    
    message = {
        "job_id": job_id,
        "num_images": num_images,
        "type": "image"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=config['rabbitmq_service']['image_generation_queue'],
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    
    connection.close()
    return True

def publish_gif_job(job_id: str):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue=config['rabbitmq_service']['gif_generation_queue'], durable=True)
    
    message = {
        "job_id": job_id,
        "type": "gif"
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=config['rabbitmq_service']['gif_generation_queue'],
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    
    connection.close()
    return True