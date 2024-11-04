import os
import os.path as op
import datetime

import PIL.Image
import torch

from diffusers import (
    ControlNetModel,
    StableDiffusionXLControlNetPipeline,
    AutoencoderKL,
)
from diffusers import EulerAncestralDiscreteScheduler

from .utils import DEFAULT_STYLE_NAME, apply_style


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Model:
    def __init__(self) -> None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.controlnet = ControlNetModel.from_pretrained(
            "xinsir/controlnet-scribble-sdxl-1.0",
            torch_dtype=dtype
        )

        self.vae = AutoencoderKL.from_pretrained(
            "madebyollin/sdxl-vae-fp16-fix",
            torch_dtype=dtype
        )

        self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
            "sd-community/sdxl-flash",
            controlnet=self.controlnet,
            vae=self.vae,
            torch_dtype=dtype,
        )
        self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
            self.pipe.scheduler.config
        )
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
        prompt: str = "",
        negative_prompt: str = "",
        style_name: str = DEFAULT_STYLE_NAME,
        num_steps: int = 25,
        guidance_scale: float = 5,
        controlnet_conditioning_scale: float = 1.0,
        seed: int = 0,
    ) -> PIL.Image.Image:
        # seed = randomize_seed_fn(seed, True)

        image = PIL.ImageOps.invert(image.convert("RGB").resize((1024, 1024)))

        # logging pics before processing
        if not op.exists(f"images/{style_name}/"):
            os.mkdir(f"images/{style_name}")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        image.save(f"images/{style_name}/{timestamp}_before.png")

        prompt, negative_prompt = apply_style(
            style_name, prompt, negative_prompt
        )

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
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        out.save(f"images/{style_name}/{timestamp}_after.png")

        return out.resize((600, 600))
