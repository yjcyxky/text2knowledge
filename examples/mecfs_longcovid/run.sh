#!/bin/bash

MODEL_NAME_VERSION="phind-codellama:34b-v2"
# MODEL_NAME_VERSION="vicuna:13b-v1.5-fp16"
MODEL_NAME=`echo $MODEL_NAME_VERSION | sed 's/:/-/'`
SCRIPT_DIR=`dirname $0`
DEST_DIR=$SCRIPT_DIR
# ALL_FILES=$(ls ${SCRIPT_DIR}/abstract/*.txt | head -n 1)
ALL_FILES=("examples/mecfs_longcovid/abstract/26411464.txt")
MODE=relationships

for file in $ALL_FILES
do
    printf "\nProcessing $file\n"
    JSON_FILENAME=`echo $file | sed 's/.txt/.json/' | sed "s/abstract/${MODE}-${MODEL_NAME}/"`
    JSON_DIR=`dirname $JSON_FILENAME`
    printf "Output file: $JSON_FILENAME\n"

    if [ ! -d ${JSON_DIR} ]; then
        mkdir -p ${JSON_DIR}
    fi

    if [ "$MODE" == "entities" ]; then
        python3 text2knowledge.py extract-entities --text-file ${file} --output-file ${JSON_FILENAME} --model-name ${MODEL_NAME_VERSION} --review
    elif [ "$MODE" == "relationships" ]; then
        python3 text2knowledge.py extract-relationships-1 --text-file ${file} --output-file ${JSON_FILENAME} --model-name ${MODEL_NAME_VERSION}
    fi
done
