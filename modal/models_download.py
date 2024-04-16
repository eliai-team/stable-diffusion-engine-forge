import subprocess

from modal import Image, Stub, web_server, Volume

PORT = 8000

models_volumn = Volume.from_name("models")

def models_download():
    DOWNLOAD_CMD = """
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/105674 -d /models/checkpoint -o realisticVisionV51_v30VAE.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/130072 -d /models/checkpoint -o realisticVisionV51_v51VAE.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/132760 -d /models/checkpoint -o absolutereality_v181.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/41 -d /models/checkpoint -o allInOnePixelModel_v1.ckpt && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/144584 -d /models/checkpoint -o asianrealisticSdlife_v90.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/177164 -d /models/checkpoint -o beautifulRealistic_v7.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/11745 -d /models/checkpoint -o ChilloutMix.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/93208 -d /models/checkpoint -o DarkSushiMix.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/128713 -d /models/checkpoint -o DreamShaper.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/10081 -d /models/checkpoint -o dvArch.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/143906 -d /models/checkpoint -o epicrealism_naturalSinRC1VAE.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/139417 -d /models/checkpoint -o M4RV3LSDUNGEONSNEWV40COMICS_mD40.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/176425 -d /models/checkpoint -o majicMIX.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/119057 -d /models/checkpoint -o meinamix_meinaV11.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/154594 -d /models/checkpoint -o moniemodAsian_v14.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/177164 -d /models/checkpoint -o realBeautifulAsian_v10.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/245627 -d /models/checkpoint -o realisticVision_V60_Inpainting.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/XpucT/Deliberate/resolve/main/Deliberate_v5.safetensors -d /models/checkpoint -o Deliberate.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_canny_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_depth_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_depth_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_inpaint_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_lineart_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_mlsd_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_mlsd_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_normalbae_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_normalbae_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_openpose_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_scribble_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_scribble_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_seg_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_seg_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_softedge_fp16.safetensors -d /models/ControlNet -o control_v11p_sd15_softedge_fp16.safetensors && \
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors -d /models/ControlNet -o control_v11f1e_sd15_tile_fp16.safetensors
"""
    subprocess.run(DOWNLOAD_CMD, shell=True)
    models_volumn.commit()

image = (
    Image.debian_slim(python_version="3.10")
    .apt_install(
        "aria2"
    )
)

stub = Stub("download_models", image=image, volumes={"/models": models_volumn})

@stub.function(timeout=3600)
def download():
    models_download()

@stub.local_entrypoint()
def main():
    download.remote()