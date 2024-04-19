import subprocess

from modal import Image, Stub, web_server, Volume, Secret

PORT = 8000

models_volumn = Volume.from_name("models")

a1111_image = (
    Image.debian_slim(python_version="3.10", force_build=False)
    .apt_install(
        "wget",
        "git",
        "aria2",
        "libgl1",
        "libglib2.0-0",
        "google-perftools",  # For tcmalloc
    )
    .env({"LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"})
    .run_commands(
        "git clone --depth 1 --branch v1.7.0 https://github.com/AUTOMATIC1111/stable-diffusion-webui /webui",
        "cd /webui/extensions && git clone https://github.com/Mikubill/sd-webui-controlnet",
        "cd /webui/extensions && git clone --single-branch --branch modal-serverless https://github.com/minhnhat0709/eliai-engine-sd-webui-ext ",
        "python -m venv /webui/venv",
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import launch_utils; launch_utils.prepare_environment()' --xformers",
        gpu="t4",
        force_build=True
    )
    .run_commands(
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import shared_init, initialize; shared_init.initialize(); initialize.initialize()' --no-download-sd-model",
        gpu="t4",
    )
    .copy_local_file("../models/ESRGAN/4xUltrasharp_4xUltrasharpV10.pt", "/webui/models/ESRGAN/4xUltrasharp_4xUltrasharpV10.pt")
    .copy_local_file("../models/Lora/add_sharpness.safetensors", "/webui/models/Lora/add_sharpness.safetensors")
    .copy_local_dir("../docker/builder/controlnet_annotation/", "/webui/models/controlnet_annotation/")
    # .run_function(models_download, shared_volumes={"/models": models_volumn})
)

# a1111_image.run_function(models_download, shared_volumes={"/models": models_volumn})

stub = Stub("forge-api", image=a1111_image, volumes={"/models": models_volumn})

env_variables = {
    "SUPABASE_ENDPOINT": "https://rtfoijxfymuizzxzbnld.supabase.co",
    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0Zm9panhmeW11aXp6eHpibmxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY1Nzc4MTQsImV4cCI6MjAxMjE1MzgxNH0.ChbqzCyTnUkrZ8VMie8y9fpu0xXB07fdSxVrNF9_psE",
    "AWS_ACCESS_KEY_ID": "445b3a76828604585e2f38f49b39188b",
    "AWS_SECRET_ACCESS_KEY": "9d5f008e8be8a9990a6cff7c6a1c78fc6498787a022cb0ea759cbd0af30c1848",
    "MAX_MEMORY_CAPACITY": "20",
    "AWS_ENDPOINT": "https://2c4e16b2cfe75a3201f2f7638084e66b.r2.cloudflarestorage.com",
    "STORAGE_DOMAIN": "https://eliai-server.eliai.vn/",
    "UPLOAD_BACKGROUND": "True"
}

secrets = Secret.from_dict(env_variables)
@stub.function(
    gpu="t4",
    cpu=2,
    memory=3072,
    timeout=3600,
    concurrency_limit=5,
    container_idle_timeout=15,
    secrets=[Secret.from_name("engine-secret")]
    # enable_memory_snapshot=True
    # Allows 100 concurrent requests per container.
    # allow_concurrent_inputs=100,
    # Keep at least one instance of the server running.
    # keep_warm=1,
)
@web_server(port=PORT, startup_timeout=1800)
def run():
    START_COMMAND = f"""
cd /webui && \
. venv/bin/activate && \
accelerate launch \
    --num_processes=1 \
    --num_machines=1 \
    --mixed_precision=fp16 \
    --dynamo_backend=inductor \
    --num_cpu_threads_per_process=6 \
    /webui/launch.py \
        --skip-prepare-environment \
        --nowebui \
        --api \
        --listen \
        --port {PORT} \
        --ckpt-dir /models/checkpoint \
        --controlnet-dir /models/ControlNet \
        --controlnet-annotator-models-path /webui/models/controlnet_annotation \
        --api-auth minhnhatdo:admin \
        --xformers \
        --no-hashing
"""
    subprocess.Popen(START_COMMAND, shell=True)
