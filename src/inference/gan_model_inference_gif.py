import os
import torch
import torch.nn as nn
from torchvision.utils import save_image
from src.inference.utils.gan_model_inference_utils import generator_class_256_256_3
import imageio
import numpy as np
from config.yaml_utils import read_yaml
from uuid import uuid4

config = read_yaml("./config/config.yaml")
CHECKPOINT_PATH = config['model_256_256_3']['model_path_256_256_3']
NUM_IMAGES = config['model_256_256_3']['number_of_images_256_256_3_to_generate']
LATENT_DIM = config['model_256_256_3']['LATENT_DIM_256_256_3']
OUTPUT_DIR = config['model_256_256_3']['output_gif_dir_256_256_3']
NUM_STEPS = config['model_256_256_3']['number_of_frames_256_256_3_in_gif']
FPS = config['model_256_256_3']['fps_of_gif_256_256_3']
os.makedirs(OUTPUT_DIR, exist_ok=True)

image_generator_256_256_3, DEVICE = generator_class_256_256_3()
image_generator_256_256_3.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=DEVICE, weights_only=True))
image_generator_256_256_3.eval()

z_start = torch.randn(1, LATENT_DIM, device=DEVICE)
z_end = torch.randn(1, LATENT_DIM, device=DEVICE)

frames = []

def generate_gif(NUM_GIF_TO_GENERATE):

    for i in range(NUM_GIF_TO_GENERATE):
        with torch.no_grad():
            for alpha in torch.linspace(0, 1, NUM_STEPS):
                z = (1 - alpha) * z_start + alpha * z_end
                img = image_generator_256_256_3(z)
                img = (img + 1) / 2
                img = img.clamp(0, 1)
                img = img[0].permute(1, 2, 0).cpu().numpy()
                img = (img * 255).astype(np.uint8)
                frames.append(img)

        imageio.mimsave(os.path.join(OUTPUT_DIR, f"generated_images_{uuid4()}.gif"), frames, fps=FPS)



def job_generate_gif(job_id):
    z_start = torch.randn(1, LATENT_DIM, device=DEVICE)
    z_end = torch.randn(1, LATENT_DIM, device=DEVICE)

    frames = []

    with torch.no_grad():
        for alpha in torch.linspace(0, 1, NUM_STEPS):
            z = (1 - alpha) * z_start + alpha * z_end
            img = image_generator_256_256_3(z)
            img = (img + 1) / 2
            img = img.clamp(0, 1)
            img = img[0].permute(1, 2, 0).cpu().numpy()
            img = (img * 255).astype(np.uint8)
            frames.append(img)

    path = f"{OUTPUT_DIR}/{job_id}_{uuid4()}.gif"
    imageio.mimsave(path, frames, fps=FPS)

    return path


