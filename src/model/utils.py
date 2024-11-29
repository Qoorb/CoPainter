import json
from pathlib import Path
import random
import numpy as np


styles_path = Path(__file__).parent / "styles.json"
with open(styles_path, "r") as f:
    style_list = json.load(f)["styles"]

styles = {k["name"]: (k["prompt"], k["negative_prompt"]) for k in style_list}

STYLE_NAMES = list(styles.keys())
DEFAULT_STYLE_NAME = "(No style)"
MAX_SEED = np.iinfo(np.int32).max


def apply_style(
    style_name: str, positive: str, negative: str = ""
) -> tuple[str, str]:
    p, n = styles.get(style_name, styles[DEFAULT_STYLE_NAME])
    return p.replace("{prompt}", positive), n + negative


def randomize_seed_fn(seed: int, randomize_seed: bool) -> int:
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    return seed
