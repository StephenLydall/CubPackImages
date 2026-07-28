from pathlib import Path

from PIL import Image
import pandas as pd

from config import (
    BASE_IMAGES,
    BACKGROUND_IMAGES,
    LOCAL_RENDER_OUTPUT,
    TO_RENDER_CSV,
)

# -----------------------------
# Configuration
# -----------------------------
BASE_IMAGE_DIR = BASE_IMAGES
BACKGROUND_DIR = BACKGROUND_IMAGES
OUTPUT_DIR = LOCAL_RENDER_OUTPUT

CANVAS_WIDTH = 856
CANVAS_HEIGHT = 140
IMG_SIZE = 136
GAP = 6

# Render limiter (set to 0 to disable)
MAX_RENDERS = 0


# -----------------------------
# Function to render one strip
# -----------------------------
def render_strip(codes, output_name):
    if not 2 <= len(codes) <= 7:
        raise ValueError("Code list must contain at least background + 1 icon, max 6 total")

    # First code is background
    bg_code = codes[0].strip()
    bg_path = BACKGROUND_DIR / f"{bg_code}.png"

    if not bg_path.exists():
        raise FileNotFoundError(f"Missing background image: {bg_code}.png")

    canvas = Image.open(bg_path).convert("RGBA")

    # Remaining codes are base images
    images = []

    for code in codes[1:]:
        code_clean = code.strip()
        path = BASE_IMAGE_DIR / f"{code_clean}.png"

        if not path.exists():
            raise FileNotFoundError(f"Missing base image: {code_clean}.png")

        images.append(Image.open(path).convert("RGBA"))

    # Calculate strip placement
    n = len(images)
    strip_width = (n * IMG_SIZE) + ((n - 1) * GAP)

    start_x = (CANVAS_WIDTH - strip_width) // 2
    start_y = (CANVAS_HEIGHT - IMG_SIZE) // 2

    x = start_x

    for img in images:
        canvas.paste(img, (x, start_y), img)
        x += IMG_SIZE + GAP

    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{output_name}.png"

    canvas.save(output_path)

    print(f"[DONE] Rendered: {output_name}.png")


# -----------------------------
# Main script
# -----------------------------
if __name__ == "__main__":

    if not TO_RENDER_CSV.exists():
        raise FileNotFoundError(f"{TO_RENDER_CSV} not found")

    df = pd.read_csv(TO_RENDER_CSV)

    if "FullCode" not in df.columns:
        raise ValueError(f"{TO_RENDER_CSV} does not contain 'FullCode' column")

    rendered_count = 0

    for _, row in df.iterrows():

        if MAX_RENDERS > 0 and rendered_count >= MAX_RENDERS:
            print(f"[STOP] Render limit reached ({MAX_RENDERS}). Stopping.")
            break

        full_code = row["FullCode"].strip()

        codes = [c.strip() for c in full_code.split(",")]

        output_name = full_code.replace(",", "_").strip()

        try:
            render_strip(codes, output_name)
            rendered_count += 1

        except Exception as e:
            print(f"[ERROR] Error rendering {full_code}: {e}")
