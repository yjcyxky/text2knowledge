## Text to Knolwedge Graph

### Article Classification

```bash
python3 text2knowledge.py classify-article --input-file ./classfication/example.json --output-file ./classfication/results/mixtral_8x22b.json -m mixtral:8x22b
```

### Strategy 1: Employ a LLM to extract entities and relations directly

Please refer to [Prompts](./text2knowledge/prompt_template.py) for more details.

If you want to extract all entities from the text, you can use the following command.

```bash
python3 text2knowledge.py extract-entities --text-file examples/text2knowledge/abstract.txt --output-file examples/text2knowledge/entities.json --model-name mistral:latest
```

If you want to extract all relations from the text, you can use the following command.

```bash
python3 text2knowledge.py extract-relations --text-file examples/text2knowledge/abstract.txt --output-file examples/text2knowledge/relationships.json --model-name mistral:latest
```

#### Issues

- [ ] How to improve the accuracy of the entity extraction?

- [ ] How to align the entities and relations? In current version, we extract entities and relations separately.

- [ ] How to align all entities to the ontology items? Such as `Hepatocellular carcinoma` --> `MONDO:0007256`. You can access the [BioPortal](https://bioportal.bioontology.org/) for learning more about the ontology items.


### Strategy 2: Employ a LLM to extract entities and relations by asking choice questions [Not Ready Yet]

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

## Launch a Chatbot Server for Text2Knowledge

NOTE: Read the [README.md](chatbot/README.md) in the `chatbot` folder for more detail [Not Ready Yet]. Or you can use another open source project [Ollama](https://ollama.ai/) or [Ollama Github](https://github.com/jmorganca/ollama) instead of our chatbot.

After you install the Ollama, you can run the following command to pull the models and launch the Ollama server.

### Pull the models

```bash
ollama pull mistral-openorca:latest

# or
bash pull_models.sh
```

### Launch the Ollama server

This step might not a required step for you. If you have installed the Ollama in macosx, you can also click the `Ollama` icon in the application folder to launch the Ollama server.

```bash
ollama serve
```

After you launch the Ollama server, you can open the following link in your browser to show all the availabel models.

http://127.0.0.1:11434/api/tags

### [Optional] Change the storage path

If you have limited storage space in your computer, you can change the storage path to another disk. More details on how to change the storage path, please refer to the [Ollama FAQs](https://github.com/ollama/ollama/blob/main/docs/faq.md#how-do-i-set-them-to-a-different-location).

```bash
echo 'OLLAMA_MODELS=/path/to/your/disk' >> ~/.bashrc
source ~/.bashrc
```

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
