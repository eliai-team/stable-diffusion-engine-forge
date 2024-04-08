# ---------------------------------------------------------------------------- #
#                         Stage 1: Download the models                         #
# ---------------------------------------------------------------------------- #
# FROM alpine/git:2.36.2 as download

# COPY docker/builder/clone.sh /clone.sh
# COPY docker/builder/clone_extensions.sh /clone_extensions.sh
# COPY docker/builder/download_controlnet_model.sh /download_controlnet_model.sh

# RUN apk --no-cache add aria2

# # Clone the repos and clean unnecessary files
# RUN . /clone.sh taming-transformers https://github.com/CompVis/taming-transformers.git 24268930bf1dce879235a7fddd0b2355b84d7ea6 && \
#     rm -rf data assets **/*.ipynb

# RUN . /clone.sh stable-diffusion-stability-ai https://github.com/Stability-AI/stablediffusion.git 47b6b607fdd31875c9279cd2f4f16b92e4ea958e && \
#     rm -rf assets data/**/*.png data/**/*.jpg data/**/*.gif

# RUN . /clone.sh CodeFormer https://github.com/sczhou/CodeFormer.git c5b4593074ba6214284d6acd5f1719b6c5d739af && \
#     rm -rf assets inputs

# RUN . /clone.sh BLIP https://github.com/salesforce/BLIP.git 48211a1594f1321b00f14c9f7a5b4813144b2fb9 && \
#     . /clone.sh k-diffusion https://github.com/crowsonkb/k-diffusion.git 5b3af030dd83e0297272d861c19477735d0317ec && \
#     . /clone.sh clip-interrogator https://github.com/pharmapsychotic/clip-interrogator 2486589f24165c8e3b303f84e9dbbea318df83e8 && \
#     . /clone.sh generative-models https://github.com/Stability-AI/generative-models 45c443b316737a4ab6e40413d7794a7f5657c19f

# RUN . /clone_extensions.sh eliai-engine-sd-webui-ext https://github.com/minhnhat0709/eliai-engine-sd-webui-ext a5b7b14dc0ae46e28337f6027fe600b3a43abcf6 && \
# RUN    . /clone_extensions.sh sd-webui-controlnet https://github.com/Mikubill/sd-webui-controlnet a13bd2febe4fae1184b548504957d19a65425a89

# RUN . /download_controlnet_model.sh


# RUN apk add --no-cache wget && \
#     wget -q -O /realisticVisionV51_v30VAE.safetensors https://civitai.com/api/download/models/105674



# ---------------------------------------------------------------------------- #
#                        Stage 3: Build the final image                        #
# ---------------------------------------------------------------------------- #
FROM python:3.10.9-slim as build_final_image

ARG SHA=5ef669de080814067961f28357256e8fe27544f4

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_PREFER_BINARY=1 \
    LD_PRELOAD=libtcmalloc.so \
    ROOT=stable-diffusion-webui \
    PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# RUN export COMMANDLINE_ARGS="--skip-torch-cuda-test --precision full --no-half"
# RUN export TORCH_COMMAND='pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/rocm5.6'



RUN apt-get update && \
    apt install -y \
    sudo fonts-dejavu-core rsync git jq moreutils aria2 wget libgoogle-perftools-dev procps libgl1 libglib2.0-0 lsof && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/* && apt-get clean -y

# RUN --mount=type=cache,target=/cache --mount=type=cache,target=/root/.cache/pip \
#     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RUN  useradd -m admin && echo "admin:admin" |  chpasswd &&  usermod -aG sudo  admin
USER admin
workdir ~/
RUN pwd

RUN git clone https://github.com/eliai-team/stable-diffusion-engine-forge.git stable-diffusion-webui && \
    cd stable-diffusion-webui 
    # git reset --hard ${SHA}
#&& \ pip install -r requirements_versions.txt

# COPY ../extensions/eliai-engine-sd-webui-ext/ ${ROOT}/extensions/eliai-engine-sd-webui-ext/

# COPY --from=download /extensions/* ${ROOT}/extensions/
# COPY --from=download /repositories/* ${ROOT}/repositories/

# COPY --from=download /realisticVisionV51_v30VAE.safetensors /runpod-volume/stable-diffusion-webui/models/Stable-diffusion/realisticVisionV51_v30VAE.safetensors
# RUN mkdir ${ROOT}/interrogate && cp ${ROOT}/repositories/clip-interrogator/data/* ${ROOT}/interrogate
# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip install -r ${ROOT}/repositories/CodeFormer/requirements.txt

# Install Python dependencies (Worker Template)
# COPY requirements_versions.txt /requirements.txt
# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip install httpx==0.24.1 && \
#     pip install --upgrade pip && \
#     pip install --upgrade -r /requirements.txt --no-cache-dir && \
#     rm /requirements.txt


COPY docker/builder/cache.py stable-diffusion-webui/cache.py
# COPY builder/controlnet_annotation/ /stable-diffusion-webui/controlnet_annotation/
# COPY builder/huggingface/ /root/.cache/huggingface/
COPY docker/builder/upscale/ stable-diffusion-webui/models/
COPY docker/builder/checkpoint/ stable-diffusion-webui/models/Stable-diffusion/

COPY docker/install.sh install.sh
RUN sudo chmod +x install.sh 
RUN install.sh


# RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' /usr/local/lib/python3.10/site-packages/basicsr/data/degradations.py
# RUN cd /stable-diffusion-webui && python cache.py --use-cpu=all --ckpt /stable-diffusion-webui/models/Stable-diffusion/realisticVisionV51_v30VAE.safetensors

# Cleanup section (Worker Template)
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# ENV SUPABASE_ENDPOINT=https://rtfoijxfymuizzxzbnld.supabase.co SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0Zm9panhmeW11aXp6eHpibmxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY1Nzc4MTQsImV4cCI6MjAxMjE1MzgxNH0.ChbqzCyTnUkrZ8VMie8y9fpu0xXB07fdSxVrNF9_psE AWS_ACCESS_KEY_ID=445b3a76828604585e2f38f49b39188b AWS_SECRET_ACCESS_KEY=9d5f008e8be8a9990a6cff7c6a1c78fc6498787a022cb0ea759cbd0af30c1848 MAX_MEMORY_CAPACITY=20
# Set permissions and specify the command to run
COPY docker/start.sh start.sh
RUN chmod +x start.sh
CMD start.sh
