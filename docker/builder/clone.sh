#!/bin/bash

set -Eeuo pipefail

directory="/repositories/$1"

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <directory_name> <git_repository> <git_branch>"
    exit 1
fi

# Check if the directory already exists
if [ -d "$directory" ]; then
    echo "Error: Directory $directory already exists."
    exit 1
fi

# Create the directory and navigate into it
mkdir -p "$directory"
cd "$directory" || exit 1

# Initialize a Git repository
git init

git config --global http.postBuffer 524288000
# Add the remote origin and fetch the specified branch with limited depth
git remote add origin "$2"
# git clone "$2"
git fetch origin "$3" --depth=1

# Reset the working directory to the specified commit/branch
git reset --hard "$3"

# Remove the Git configuration and history
rm -rf .git

echo "Extension '$1' successfully cloned and initialized in '$directory'."
