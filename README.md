## Installation

```bash
conda create -n text2knowledge python=3.10 openjdk=11
```

## Pdf to Text
### Step 1: Launch the grobid server

If you have any questions about how to launch the grobid server, please refer to https://grobid.readthedocs.io/en/latest/Grobid-service/.

If you encounter the following error when launching the grobid server, please download grobid manually and put it in the `pdf2json` folder, and then rename it to `grobid-0.8.0.zip` (The grobid version we use is `0.8.0`).

The download link of grobid is [grobid-0.8.0.zip](https://github.com/kermitt2/grobid/archive/refs/tags/grobid-0.8.0.zip). After finished, please run `bash launch_grobid.sh` again.

If you cannot run grobid server successfully, please use docker to run grobid server. If you only want to try the extraction function, you can skip the `Step 1` and use the public grobid server (https://kermitt2-grobid.hf.space) instead in `Step 2`.

```bash
cd pdf2json
bash launch_grobid.sh

# or

docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
```

### Step 2: Convert pdf to json/figure/table/text

We use the [grobid](https://github.com/kermitt2/grobid) and [scipdf_parser](git+https://github.com/titipata/scipdf_parser) to convert pdf to json, figure, table, and text. If you want to know more about how to convert pdf to json, figure, table, and text, please refer to `grobid` and `scipdf_parser`. If you want to convert a large number of pdfs to json, figure, table, and text, please use a local grobid server instead of a public grobid server (https://kermitt2-grobid.hf.space).

```bash
python3 text2knowledge.py pdf2text --pdf-file ../examples/pdfs/16451124.pdf --output-dir ../examples/extracted_pdfs/ --grobid-url https://kermitt2-grobid.hf.space
```

After running the above command, you will get the following files:

```bash
examples/extracted_pdfs/16451124
    |-- 16451124.json               # Abstract and body text
    |-- pdf                         # Original pdf, just for convenience
    |   |-- 16451124.pdf
    |-- figures
    |   |-- 16451124-Figure1-1.png  # Figure 1 in the paper
    |   |-- 16451124-Figure2-1.png
    |   |-- 16451124-Figure3-1.png
    |   |-- 16451124-Figure4-1.png
    |   |-- 16451124-Figure5-1.png
    |-- data
    |   |-- 16451124.json           # Abstract and body text, same as 16451124.json, just for convenience
```

## Text to Knolwedge Graph
### Strategy 1: Employ the LLM to extract entities and relations directly

### Strategy 2: Employ the LLM ask choice questions to extract entities and relations

#### Introduction

A new solution to convert text to knowledge graph

1. `Extract` all biomedical entities from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)
2. Convert all preset ontology items to `embeddings`
3. `Map` all extracted entities to the ontology items by computing the similarity between the embeddings, and then pick up the top N similar ontology items for each entity
4. Use a more precise method to `re-rank` the top N similar ontology items for each entity and pick up the top 1
5. `Generate questions` from the mapped ontology items. If we have ten entities, we can generate `C(10, 2) = 10! / [2!(10-2)!] = (10 _ 9) / (2 _ 1) = 45` questions. We can reduce the number of questions based on our needs, such as we only care about the specific entities.
6. `Pick up the answer for each question` from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)

#### Improvement plan

1. Fine-tune embedding algorithm for biomedical entities
2. Select the most suitable similarity algorithm
3. Select a suitable re-ranking algorithm
4. Improve the prompts for generating questions based on the characteristics of the large language model
