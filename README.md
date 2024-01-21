## Benchmarking Datasets and Tools for Biomedical NLP

1. Biomedical Datasets: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-022-04688-w/tables/2
2. N2C2 NLP Dataset: https://portal.dbmi.hms.harvard.edu
3. BC5CDR (BioCreative V CDR corpus): https://paperswithcode.com/dataset/bc5cdr
4. BC4CHEMD (BioCreative IV Chemical compound and drug name recognition): https://paperswithcode.com/dataset/bc4chemd
5. BioNLP: https://aclanthology.org/venues/bionlp/
6. PubTator: https://www.ncbi.nlm.nih.gov/research/pubtator3/
7. BioNLP-Corpus: https://github.com/bionlp-hzau/BioNLP-Corpus
8. BioBERT & Bern: https://github.com/dmis-lab/bern
9. BioRED: https://academic.oup.com/bib/article/23/5/bbac282/6645993

## Installation

```bash
conda create -n text2knowledge python=3.10 openjdk=11
```

## Pdf to Text

### Step 1: Launch the grobid server

```bash
cd pdf2json
bash launch_grobid.sh

# or

docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
```

### Step 2: Convert pdf to json/figure/table/text

We use the [grobid](https://github.com/kermitt2/grobid)) and [scipdf_parser](git+https://github.com/titipata/scipdf_parser) to convert pdf to json, figure, table, and text. If you want to know more about how to convert pdf to json, figure, table, and text, please refer to `grobid` and `scipdf_parser`.

```bash
python3 text2knowledge.py pdf2text --pdf-file ../examples/pdfs/16451124.pdf --output-dir <output-dir>
```

## Text to Knolwedge Graph

### Introduction

A new solution to convert text to knowledge graph

1. `Extract` all biomedical entities from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)
2. Convert all preset ontology items to `embeddings`
3. `Map` all extracted entities to the ontology items by computing the similarity between the embeddings, and then pick up the top N similar ontology items for each entity
4. Use a more precise method to `re-rank` the top N similar ontology items for each entity and pick up the top 1
5. `Generate questions` from the mapped ontology items. If we have ten entities, we can generate `C(10, 2) = 10! / [2!(10-2)!] = (10 _ 9) / (2 _ 1) = 45` questions. We can reduce the number of questions based on our needs, such as we only care about the specific entities.
6. `Pick up the answer for each question` from the text by using a large language model (e.g. ChatGPT4, Vicuna, etc.)

### Improvement plan

1. Fine-tune embedding algorithm for biomedical entities
2. Select the most suitable similarity algorithm
3. Select a suitable re-ranking algorithm
4. Improve the prompts for generating questions based on the characteristics of the large language model
