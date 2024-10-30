import os
import os.path as op
import datetime
import random

import PIL.Image
import torch
import torchvision.transforms.functional as TF

from diffusers import ControlNetModel, StableDiffusionXLControlNetPipeline, AutoencoderKL
from diffusers import DDIMScheduler, EulerAncestralDiscreteScheduler
from diffusers.utils import load_image
from pathlib import Path
from PIL import Image, ImageOps
import torch
import numpy as np


MAX_SEED = np.iinfo(np.int32).max

style_list = [
    {
        "name": "(No style)",
        "prompt": "{prompt}",
        "negative_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",
    },
    {
        "name": "Cinematic",
        "prompt": "cinematic still {prompt} . emotional, harmonious, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
        "negative_prompt": "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    },
    {
        "name": "3D Model",
        "prompt": "professional 3d model {prompt} . octane render, highly detailed, volumetric, dramatic lighting",
        "negative_prompt": "ugly, deformed, noisy, low poly, blurry, painting",
    },
    {
        "name": "Anime",
        "prompt": "anime artwork {prompt} . anime style, key visual, vibrant, studio anime,  highly detailed",
        "negative_prompt": "photo, deformed, black and white, realism, disfigured, low contrast",
    },
    {
        "name": "Digital Art",
        "prompt": "concept art {prompt} . digital artwork, illustrative, painterly, matte painting, highly detailed",
        "negative_prompt": "photo, photorealistic, realism, ugly",
    },
    {
        "name": "Photographic",
        "prompt": "cinematic photo {prompt} . 35mm photograph, film, bokeh, professional, 4k, highly detailed",
        "negative_prompt": "drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
    },
    {
        "name": "Pixel art",
        "prompt": "pixel-art {prompt} . low-res, blocky, pixel art style, 8-bit graphics",
        "negative_prompt": "sloppy, messy, blurry, noisy, highly detailed, ultra textured, photo, realistic",
    },
    {
        "name": "Fantasy art",
        "prompt": "ethereal fantasy concept art of  {prompt} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy",
        "negative_prompt": "photographic, realistic, realism, 35mm film, dslr, cropped, frame, text, deformed, glitch, noise, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, sloppy, duplicate, mutated, black and white",
    },
    {
        "name": "Neonpunk",
        "prompt": "neonpunk style {prompt} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional",
        "negative_prompt": "painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
    },
    {
        "name": "Manga",
        "prompt": "manga style {prompt} . vibrant, high-energy, detailed, iconic, Japanese comic style",
        "negative_prompt": "ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, Western comic style",
    },
]

styles = {k["name"]: (k["prompt"], k["negative_prompt"]) for k in style_list}
STYLE_NAMES = list(styles.keys())
DEFAULT_STYLE_NAME = "(No style)"

def apply_style(style_name: str, positive: str, negative: str = "") -> tuple[str, str]:
    p, n = styles.get(style_name, styles[DEFAULT_STYLE_NAME])
    return p.replace("{prompt}", positive), n + negative

def randomize_seed_fn(seed: int, randomize_seed: bool) -> int:
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    return seed


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Model:
    def __init__(self) -> None:
        self.controlnet = ControlNetModel.from_pretrained(
            "xinsir/controlnet-scribble-sdxl-1.0",
            torch_dtype=torch.float16
        )

        self.vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)

        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "sd-community/sdxl-flash",
            controlnet=self.controlnet,
            vae=self.vae,
            torch_dtype=torch.float16,
        )
        self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(device)

    # def latents_to_rgb(self, latents):
    #     weights = (
    #         (60, -60, 25, -70),
    #         (60,  -5, 15, -50),
    #         (60,  10, -5, -35)
    #     )

    #     weights_tensor = torch.t(torch.tensor(weights, dtype=latents.dtype).to(latents.device))
    #     biases_tensor = torch.tensor((150, 140, 130), dtype=latents.dtype).to(latents.device)
    #     rgb_tensor = torch.einsum("...lxy,lr -> ...rxy", latents, weights_tensor) + biases_tensor.unsqueeze(-1).unsqueeze(-1)
    #     image_array = rgb_tensor.clamp(0, 255)[0].byte().cpu().numpy()
    #     image_array = image_array.transpose(1, 2, 0)

    #     return PIL.Image.Image.fromarray(image_array)
    
    # def decode_tensors(self, pipe, step, timestep, callback_kwargs):
    #     latents = callback_kwargs["latents"]
        
    #     image = self.latents_to_rgb(latents)
    #     image.save(f"{step}.png")
    
    #     return callback_kwargs

    def run(
        self,
        image: PIL.Image.Image,
        prompt: str = '',
        negative_prompt: str = '',
        style_name: str = DEFAULT_STYLE_NAME,
        num_steps: int = 25,
        guidance_scale: float = 5,
        controlnet_conditioning_scale: float = 1.0,
        seed: int = 0,
    ) -> PIL.Image.Image:
        # seed = randomize_seed_fn(seed, True)
        
        image = PIL.ImageOps.invert(image.convert("RGB").resize((1024, 1024)))

        # logging pics before processing
        if not op.exists(f'images/{style_name}/'): os.mkdir(f'images/{style_name}')
        image.save(f'images/{style_name}/{str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))}_before.png')
        
        prompt, negative_prompt = apply_style(style_name, prompt, negative_prompt)
    
        generator = torch.Generator(device=device).manual_seed(seed)
        
        out = self.pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=image,
        num_inference_steps=num_steps,
        generator=generator,
        controlnet_conditioning_scale=controlnet_conditioning_scale,
        guidance_scale=guidance_scale,
        # callback_on_step_end=self.decode_tensors,
        # callback_on_step_end_tensor_inputs=["latents"],
        ).images[0]

        # logging pics after processing
        out.save(f'images/{style_name}/{str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))}_after.png')
    
        return out.resize((600, 600))
