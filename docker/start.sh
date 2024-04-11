#!/bin/bash

echo "Worker Initiated"

# echo "Starting WebUI API"
# python /stable-diffusion-webui/webui.py --controlnet-annotator-models-path  /stable-diffusion-webui/controlnet_annotation --ckpt /runpod-volume/stable-diffusion-webui/models/Stable-diffusion/realisticVisionV51_v30VAE.safetensors  --ckpt-dir /runpod-volume/stable-diffusion-webui/models/Stable-diffusion --lora-dir /runpod-volume/stable-diffusion-webui/models/Lora  --skip-python-version-check --skip-torch-cuda-test --skip-install  --lowram --opt-sdp-attention --disable-safe-unpickle --port 3000 --api --nowebui --skip-version-check  --no-hashing --no-download-sd-model &

# echo "Starting RunPod Handler"
# python -u /rp_handler.py

# --controlnet-dir /runpod-volume/stable-diffusion-webui/models/ControlNet


export SUPABASE_ENDPOINT=https://rtfoijxfymuizzxzbnld.supabase.co SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0Zm9panhmeW11aXp6eHpibmxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY1Nzc4MTQsImV4cCI6MjAxMjE1MzgxNH0.ChbqzCyTnUkrZ8VMie8y9fpu0xXB07fdSxVrNF9_psE AWS_ACCESS_KEY_ID=445b3a76828604585e2f38f49b39188b AWS_SECRET_ACCESS_KEY=9d5f008e8be8a9990a6cff7c6a1c78fc6498787a022cb0ea759cbd0af30c1848 MAX_MEMORY_CAPACITY=20 AWS_ENDPOINT=https://2c4e16b2cfe75a3201f2f7638084e66b.r2.cloudflarestorage.com STORAGE_DOMAIN=https://eliai-server.eliai.vn/

cd /stable-diffusion-webui

git clone https://github.com/minhnhat0709/eliai-engine-sd-webui-ext extensions/eliai-engine-sd-webui-ext
cd extensions/eliai-engine-sd-webui-ext
git checkout auto-scale-engine
cd ../..

while true; do
	if ! lsof -i:5001 -sTCP:LISTEN > /dev/null
	then
    		python ./webui.py --nowebui --api --xformers --port 5001 --listen > /engine_1.txt 2>&1 &
	fi

	if ! lsof -i:5002 -sTCP:LISTEN > /dev/null
	then
    		python ./webui.py --nowebui --api --xformers --port 5002 --listen > /engine_2.txt 2>&1 &
	fi
	
	sleep 1m
done