#!/bin/bash

# Collect the models to download
if [ $# -ne 0 ]; then
    # Split the input string by white space
    IFS=' ' read -r -a models <<< "$@"
else
    models=("llama3.1:70b" "mistral:7b" "mixtral:8x7b" "mixtral:8x22b")
fi

echo "Models to download: ${models[@]}"

# Pull the models
for model in "${models[@]}"; do
    echo "Executing: ollama pull $model"
    if ollama pull "$model"; then
        echo "Successfully downloaded $model"
    else
        echo "Error occurred while downloading $model"
    fi
done
