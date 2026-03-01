import os
import torch
from torchvision.utils import save_image
from src.inference.utils.gan_model_inference_utils import generator_class_256_256_3
from uuid import uuid4
from config.yaml_utils import read_yaml
from src.database_operation.media_storage import upload_image_to_cloudinary

config = read_yaml("./config/config.yaml")
CHECKPOINT_PATH = config['model_256_256_3']['model_path_256_256_3']
NUM_IMAGES = config['model_256_256_3']['number_of_images_256_256_3_to_generate']
LATENT_DIM = config['model_256_256_3']['LATENT_DIM_256_256_3']
OUTPUT_DIR = config['model_256_256_3']['output_dir_256_256_3']
os.makedirs(OUTPUT_DIR, exist_ok=True)

image_generator_256_256_3, DEVICE = generator_class_256_256_3()
image_generator_256_256_3.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=DEVICE, weights_only=True))
image_generator_256_256_3.eval()

def generate_images(NUM_IMAGES_TO_GENERATE):
    with torch.no_grad():
        z = torch.randn(NUM_IMAGES_TO_GENERATE, LATENT_DIM, device=DEVICE)
        images = image_generator_256_256_3(z)
        images = (images + 1) / 2
        images = images.clamp(0, 1)

    for i in range(NUM_IMAGES_TO_GENERATE):
        save_image(images[i], f"{OUTPUT_DIR}/anime_{uuid4()}.png")


def job_generate_image(job_id, num_images=1):
    with torch.no_grad():
        z = torch.randn(num_images, LATENT_DIM, device=DEVICE)
        images = image_generator_256_256_3(z)
        images = (images + 1) / 2
        images = images.clamp(0, 1)

    urls = []
    for i in range(num_images):
        path = f"{OUTPUT_DIR}/{job_id}_{i}.png"
        save_image(images[i], path)
        url = upload_image_to_cloudinary(images[i])
        urls.append(url)

    return urls

