import click
import os
import json
import logging
import pandas as pd
from text2knowledge.utils import init_logger, EmbeddingGenerator
from text2knowledge.strategy1 import (
    extract_entities as extract_entities_from_text,
    extract_relations as extract_relations_from_text,
    classify_article as classify_article_from_text,
    correct_extracted_entities,
)

logging.basicConfig(level=logging.WARNING)
logger = init_logger(__name__)

cli = click.Group()

@cli.command(help="Extract biomedical entities from a given text or a set of texts.")
@click.option(
    "--text-file",
    "-i",
    help="Text file.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file.",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
@click.option(
    "--model-name",
    "-m",
    help="Model name. You can use any model which supported by ollama.ai. If you don't know which models are available, you can use the command `ollama list` to list all installed models or visit https://ollama.ai/library. Default: mistral-openorca:latest",
    default="mistral-openorca:latest",
)
@click.option(
    "--metadata",
    "-d",
    type=click.Path(exists=False, file_okay=False, dir_okay=False),
    help="A metadata file which contains a json object. Such as {'source': 'pubmed', 'pmid': '123456', 'type': 'abstract', ...}, you can specify any key-value pairs you want.",
)
@click.option(
    "--review",
    "-r",
    is_flag=True,
    help="Review the entities and make corrections.",
)
@click.option(
    "--ontology-embedding-file",
    "-e",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help="A file which contains ontology embeddings, which is a biomedgps-format file but with an embedding column.",
)
@click.option(
    "--embedding-model-name",
    "-n",
    help="Embedding model name. Default: mistralai/Mistral-7B-v0.1",
    default="mistralai/Mistral-7B-v0.1",
)
def extract_entities(text_file: str, output_file: str, model_name: str, metadata: str, review: bool = False, ontology_embedding_file: str | None = None, embedding_model_name: str = "mistralai/Mistral-7B-v0.1"):
    print("Extracting entities using the model %s..." % model_name)
    if metadata and os.path.exists(metadata):
        with open(metadata, "r") as f:
            metadata = f.read()
    else:
        metadata = {} # type: ignore

    def extract(text):
        if os.path.exists(output_file):
            if review:
                entities = json.load(open(output_file))

                if entities:
                    print(
                        f"Entities found in the {text_file} file, so we will review them."
                    )
                    entities = correct_extracted_entities(
                        text=text,
                        model=model_name,
                        metadata=metadata,
                        entities=entities,
                        is_list=True,
                    )
                else:
                    print(
                        f"No entities found for the {text_file} file, please extract the entities first."
                    )
                    return
            else:
                print(
                    f"Entities found in the {text_file} file, so we will skip the extraction."
                )
                return
        else:
            if ontology_embedding_file and os.path.exists(ontology_embedding_file):
                df = pd.read_csv(ontology_embedding_file, sep="\t")
                df["embedding"] = df["embedding"].apply(
                    lambda x: [float(i) for i in x.split("|")]
                )
            else:
                df = None

            entities = extract_entities_from_text(
                text,
                model=model_name,
                metadata=metadata,
                embeddings=df,
                embedding_model_name=embedding_model_name,
            )

        return entities

    if os.path.dirname(output_file) and not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(text_file, "r") as f:
        text = f.read()

    entities = extract(text)

    if entities:
        output_file = output_file if not review else output_file.replace(".json", "_reviewed.json")
        with open(output_file, "w") as f:
            entities_str = json.dumps(entities, indent=4)
            f.write(entities_str)
    else:
        print(f"No entities found for the {text_file} file.")


@cli.command(help="Extract relationships between biomedical entities from a given text using strategy 1.")
@click.option(
    "--text-file",
    "-a",
    help="Text file which contains a paragraph.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file.",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
@click.option(
    "--model-name",
    "-m",
    help="Model name. You can use any model which supported by ollama.ai. If you don't know which models are available, you can use the command `ollama list` to list all installed models or visit https://ollama.ai/library. Default: mistral-openorca:latest",
    default="mistral-openorca:latest",
)
@click.option(
    "--metadata",
    "-d",
    type=click.Path(exists=False, file_okay=False, dir_okay=False),
    help="A metadata file which contains a json object. Such as {'source': 'pubmed', 'pmid': '123456', 'type': 'abstract', ...}, you can specify any key-value pairs you want.",
)
def extract_relations(text_file: str, model_name: str, metadata: str, output_file: str):
    if metadata and os.path.exists(metadata):
        with open(metadata, "r") as f:
            metadata = f.read()
    else:
        metadata = {} # type: ignore

    with open(text_file, "r") as f:
        text = f.read()
        relations = extract_relations_from_text(
            text, model=model_name, metadata=metadata
        )

    if relations:
        with open(output_file, "w") as f:
            relations_str = json.dumps(relations, indent=4)
            f.write(relations_str)
    else:
        print(f"No relations found for the {text_file} file.")


@cli.command(
    help="Classify the given text into a specific category using the model."
)
@click.option(
    "--input-file",
    "-i",
    help="A json file which contains a list of texts.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file.",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
@click.option(
    "--model-name",
    "-m",
    help="Model name. You can use any model which supported by ollama.ai. If you don't know which models are available, you can use the command `ollama list` to list all installed models or visit https://ollama.ai/library. Default: mistral-openorca:latest",
    default="mistral-openorca:latest",
)
def classify_article(input_file: str, output_file: str, model_name: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The {input_file} file does not exist.")

    if os.path.exists(output_file):
        logger.info("The output file exists, so we will load the previous outputs.")
        with open(output_file, "r") as f:
            outputs = json.load(f)
    else:
        outputs = []

    processed_titles = set([o.get("title") for o in outputs])
    with open(input_file, "r") as f:
        data = json.load(f)
        for idx, d in enumerate(data):
            title = d.get("title", "")

            if title in processed_titles:
                logger.info(f"Classifying the {idx + 1}th / {len(data)} text: {title} has been processed, so we skip it.")
                continue

            abstract = d.get("abstract", "")
            text = f"{title}\n{abstract or 'No abstract found.'}"
            logger.info(f"Classifying the {idx + 1}th / {len(data)} text: {title}")
            outputs.append(classify_article_from_text(text, model=model_name))

            if idx > 0 and idx % 10 == 0:
                with open(output_file, "w") as f:
                    outputs_str = json.dumps(outputs, indent=4)
                    f.write(outputs_str)

    if outputs:
        with open(output_file, "w") as f:
            outputs_str = json.dumps(outputs, indent=4)
            f.write(outputs_str)
    else:
        logger.info(f"No valid outputs found for the {input_file} file.")


@cli.command(
    help="Generate embeddings for the given entities using the model."
)
@click.option(
    "--input-file",
    "-i",
    help="A tsv file which contains a list of entities.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--output-file",
    "-o",
    help="Output file.",
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
)
@click.option(
    "--model-name",
    "-m",
    help="Model name.",
    default="mistralai/Mistral-7B-v0.1",
)
def generate_embeddings(input_file: str, output_file: str, model_name: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The {input_file} file does not exist.")

    with open(input_file, "r") as f:
        entities_df = pd.read_csv(f, sep="\t")
        embedding_generator = EmbeddingGenerator(model_name=model_name)
        entities_df["embedding"] = entities_df["name"].apply(lambda x: embedding_generator.gen_text_embedding(x).tolist())
        entities_df["embedding"] = entities_df["embedding"].apply(lambda x: "|".join([str(i) for i in x]))

    if entities_df is not None:
        entities_df.to_csv(output_file, sep="\t", index=False)

if __name__ == "__main__":
    # Add the directory which contains this file to the python path
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    cli()
