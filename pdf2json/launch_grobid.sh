#!/bin/bash

# download GROBID if directory does not exist
declare -r GROBID_VERSION="0.8.0" # or change to current stable version

if [ ! -f "grobid-${GROBID_VERSION}.zip" ]; then
  echo "Downloading GROBID ${GROBID_VERSION}..."
  wget https://github.com/kermitt2/grobid/archive/refs/tags/${GROBID_VERSION}.zip -O "grobid-${GROBID_VERSION}.zip"
fi

if [ ! -d grobid-${GROBID_VERSION} ]; then
  echo "Unzipping GROBID ${GROBID_VERSION}..."
  unzip "grobid-${GROBID_VERSION}.zip"
fi

# run GROBID
cd grobid-${GROBID_VERSION} || exit
echo "Running GROBID ${GROBID_VERSION}..."
./gradlew run