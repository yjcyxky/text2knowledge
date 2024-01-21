## Installation

```bash
conda create -n text2knowledge python=3.10 openjdk=11

git clone https://github.com/yjcyxky/text2knowledge.git
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
python3 text2knowledge.py pdf2text --pdf-file ../examples/pdf2json/pdfs/16451124.pdf --output-dir ../examples/pdf2json/extracted_pdfs/ --grobid-url https://kermitt2-grobid.hf.space
```

After running the above command, you will get the following files:

```bash
examples/pdf2json/extracted_pdfs/16451124
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

## Launch a Chatbot Server for Text2Knowledge

Read the [README.md](chatbot/README.md) in the `chatbot` folder for more detail [Not Ready Yet]. So you can use another open source project [Ollama](https://ollama.ai/) or [Ollama Github](https://github.com/jmorganca/ollama) instead of our chatbot.

After you install the Ollama, you can run the following command to launch the Ollama server.

```bash
ollama pull mistral-openorca:latest

ollama serve
```

After you launch the Ollama server, you can open the following link in your browser to show all the availabel models.

http://127.0.0.1:11434/api/tags


## Text to Knolwedge Graph
### Strategy 1: Employ a LLM to extract entities and relations directly

Please refer to [Prompts](./text2knowledge/prompt_template.py) for more details.

If you want to extract all entities from the text, you can use the following command.

```bash
python3 text2knowledge.py extract-entities --text-file examples/text2knowledge/abstract.txt --output-file examples/text2knowledge/entities.json --model-name mistral:latest
```

If you want to extract all relations from the text, you can use the following command.

```bash
python3 text2knowledge.py extract-relationships-1 --text-file examples/text2knowledge/abstract.txt --output-file examples/text2knowledge/relationships.json --model-name mistral:latest
```

#### Issues

- [ ] How to improve the accuracy of the entity extraction?

- [ ] How to align the entities and relations? In current version, we extract entities and relations separately.

- [ ] How to align all entities to the ontology items? Such as `Hepatocellular carcinoma` --> `MONDO:0007256`. You can access the [BioPortal](https://bioportal.bioontology.org/) for learning more about the ontology items.


### Strategy 2: Employ a LLM to extract entities and relations by asking choice questions

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

## Benchmarking

### Datasets

Benchmarking Datasets and Tools for Biomedical NLP

1. Biomedical Datasets: https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-022-04688-w/tables/2
2. N2C2 NLP Dataset: https://portal.dbmi.hms.harvard.edu
3. BC5CDR (BioCreative V CDR corpus): https://paperswithcode.com/dataset/bc5cdr
4. BC4CHEMD (BioCreative IV Chemical compound and drug name recognition): https://paperswithcode.com/dataset/bc4chemd
5. BioNLP: https://aclanthology.org/venues/bionlp/
6. PubTator: https://www.ncbi.nlm.nih.gov/research/pubtator3/
7. BioNLP-Corpus: https://github.com/bionlp-hzau/BioNLP-Corpus
8. BioBERT & Bern: https://github.com/dmis-lab/bern
9. BioRED: https://academic.oup.com/bib/article/23/5/bbac282/6645993

### References

You can refer to these [papers/models/companies](./REFERENCES.md) for more details.

## Contribution Guidelines

We welcome and appreciate any contributions from the community members. If you wish to contribute to Text2Knowledge, please follow these steps:

1. Fork the repository and create your branch.
2. Make changes in your branch.
3. Submit a Pull Request.

Please ensure that your code adheres to the project's coding style and quality standards before submitting your contribution.

## License

Text2Knowledge is released under the MIT License. For more details, please refer to the `LICENSE.md` file in the repository.
