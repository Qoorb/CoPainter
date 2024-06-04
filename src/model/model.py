import random
import asyncio
import numpy as np
import PIL.Image
import torch
import torchvision.transforms.functional as TF
from diffusers import (
    AutoencoderKL,
    EulerAncestralDiscreteScheduler,
    StableDiffusionXLAdapterPipeline,
    T2IAdapter,
)


MAX_SEED = np.iinfo(np.int32).max

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Project running on device: ", device)

style_list = [
    {
        "name": "(No style)",
        "prompt": "{prompt}",
        "negative_prompt": "",
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


class Model:
    def __init__(self) -> None:
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        self.adapter = T2IAdapter.from_pretrained(
            "TencentARC/t2i-adapter-sketch-sdxl-1.0", torch_dtype=torch.float16, variant="fp16"
        )
        self.scheduler = EulerAncestralDiscreteScheduler.from_pretrained(
            self.model_id, subfolder="scheduler"
        )
        self.pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
            self.model_id,
            vae=AutoencoderKL.from_pretrained(
                "madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16
            ),
            adapter=self.adapter,
            scheduler=self.scheduler,
            torch_dtype=torch.float16,
            variant="fp16",
        )
        self.pipe.to(device)

    async def run(
        self,
        image: PIL.Image.Image,
        prompt: str = '',
        negative_prompt: str = '',
        style_name: str = DEFAULT_STYLE_NAME,
        num_steps: int = 25,
        guidance_scale: float = 5,
        adapter_conditioning_scale: float = 0.8,
        adapter_conditioning_factor: float = 0.8,
        seed: int = 0
    ) -> PIL.Image.Image:
        seed = randomize_seed_fn(seed, True)

        image = image.convert("RGB")
        image = TF.to_tensor(image) > 0.5
        image = TF.to_pil_image(image.to(torch.float32))

        prompt, negative_prompt = apply_style(style_name, prompt, negative_prompt)

        generator = torch.Generator(device=device).manual_seed(seed)
        
        loop = asyncio.get_event_loop()
        out = await loop.run_in_executor(
            None,
            lambda: self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image,
                num_inference_steps=num_steps,
                generator=generator,
                guidance_scale=guidance_scale,
                adapter_conditioning_scale=adapter_conditioning_scale,
                adapter_conditioning_factor=adapter_conditioning_factor,
            ).images[0]
        )

        return out
