## Introduction

You can access https://grobid.readthedocs.io/en/latest/Introduction/ for more information about the project.

## Installation

```bash
conda create -n text2knowledge python=3.10 openjdk=11

conda activate text2knowledge
```

## Launch the grobid server

```bash
cd pdf2json
bash launch_grobid.sh
```

or 
    
```bash
cd pdf2json
docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
```
