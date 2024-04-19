#!/bin/bash
cd /stable-diffusion-webui

while true; do
  file="./params.txt"

  # Check if the file exists
  if [ -e "$file" ]; then
    # Get the current timestamp
    current_time=$(date +%s)

    # Get the modification time of the file in seconds
    file_modification_time=$(stat -c %Y "$file")

    # Calculate the time difference in seconds
    time_difference=$((current_time - file_modification_time))

    # Check if the file hasn't been modified in the last 180 seconds and make sure it's not shut down immediately
    if [ "$time_difference" -ge 180 ]; then
        echo "The file has not been modified in the last 180 seconds."
        /vast destroy instance $CONTAINER_ID --api-key $CONTAINER_API_KEY
    else
        echo "The file has been modified in the last 180 seconds."
    fi
  else
    echo "File does not exist."
  fi
  
  sleep 1m
done