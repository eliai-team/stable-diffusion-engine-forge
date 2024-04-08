cd ~/stable-diffusion-webui



while true; do
	if ! lsof -i:5456 -sTCP:LISTEN > /dev/null
	then
    	./webui.sh --nowebui --api --xformers --port 5456 > ~/engine_1.txt 2>&1 &
	else
      break
  fi
	
	sleep 1m
done