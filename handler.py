from PIL import Image
import torch
import io
import time
from image_gen_aux import UpscaleWithModel
import runpod
import base64
MODEL_ID = "Phips/4xNomosWebPhoto_RealPLKSR"
TILE_W, TILE_H = 1024, 1024
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
UPSCALER = UpscaleWithModel.from_pretrained(MODEL_ID).to(DEVICE)


def handler(event):
    # Extract input data
    print(f"Worker Start")
    input = event['input']

    base64_image = input.get('image')
    image_data = base64.b64decode(base64_image)
    image_file = io.BytesIO(image_data)
    pil_img = Image.open(image_file).convert("RGB")

    # Perform upscaling
    start_time = time.time()
    print("upscaling..")
    upscaled_img = UPSCALER(pil_img, tiling=True, tile_width=TILE_W, tile_height=TILE_H)
    duration = time.time() - start_time
    print(f"Upscaling time: {duration:.2f} seconds")
    buffer = io.BytesIO()
    upscaled_img.save(buffer, format="JPEG")
    buffer.seek(0)

    # Encode to base64
    img_bytes = buffer.read()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64


if __name__  == "__main__":
    runpod.serverless.start({"handler": handler})
