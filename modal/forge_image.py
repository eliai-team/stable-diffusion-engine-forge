import subprocess

from modal import Image, Stub, web_server

PORT = 8000


a1111_image = (
    Image.debian_slim(python_version="3.10")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "google-perftools",  # For tcmalloc
    )
    .env({"LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"})
    .run_commands(
        "git clone https://github.com/eliai-team/stable-diffusion-engine-forge /webui",
        "python -m venv /webui/venv",
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import launch_utils; launch_utils.prepare_environment()' --xformers",
        gpu="t4",
        # force_build=True
    )
    .run_commands(
        "cd /webui && . venv/bin/activate && "
        + "python -c 'from modules import initialize; from modules_forge.initialization import initialize_forge; initialize_forge(); initialize.imports(); initialize.initialize()'",
        gpu="t4",
    )
)

stub = Stub("forge-api", image=a1111_image)

@stub.function(
    gpu="t4",
    cpu=2,
    memory=4092,
    timeout=800,
    concurrency_limit=5
    # Allows 100 concurrent requests per container.
    # allow_concurrent_inputs=100,
    # Keep at least one instance of the server running.
    # keep_warm=1,
)
@web_server(port=PORT, startup_timeout=180)
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
        --port {PORT}
"""
    subprocess.Popen(START_COMMAND, shell=True)
