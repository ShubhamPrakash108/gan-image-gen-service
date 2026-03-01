from config.yaml_utils import read_yaml
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import io
from PIL import Image
import numpy as np
import requests

load_dotenv()

config = read_yaml("config/config.yaml")

CLOUDINARY_FOLDER_NAME = config['media_storage_service']['cloudinary_folder_name']
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

def upload_image_to_cloudinary(image_tensor):
    """
    Uploads a PyTorch image tensor directly to Cloudinary
    without saving to disk.
    """
    try:
        image_np = image_tensor.cpu().permute(1, 2, 0).numpy()
        image_np = (image_np * 255).clip(0, 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)

        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)

        response = cloudinary.uploader.upload(
            buffer,
            folder=CLOUDINARY_FOLDER_NAME,
            resource_type="image"
        )

        return response["secure_url"]

    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None


def retrieve_image_from_cloudinary(url):
    """
    Retrieves an image from Cloudinary by URL.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error retrieving image: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error retrieving image from Cloudinary: {e}")
        return None