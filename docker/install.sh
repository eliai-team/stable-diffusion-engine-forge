cd /stable-diffusion-webui

python -c "from modules import launch_utils; launch_utils.prepare_environment();" --skip-torch-cuda-test --xformers
pip cache purge
# ./webui.sh --nowebui --api --xformers --port 5456 --skip-torch-cuda-test --building

# while true; do
# 	if ! lsof -i:5456 -sTCP:LISTEN > /dev/null
# 	then
#     	./webui.sh --nowebui --api --xformers --port 5456 --skip-torch-cuda-test --building
# 	else
#       break
#   fi
	
# 	sleep 1m
# done