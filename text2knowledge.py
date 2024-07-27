import click
import os
import json
import logging
from text2knowledge.utils import get_valid_entities, init_logger
from text2knowledge.strategy1 import extract_concepts, graph_prompt, classify
from text2knowledge.strategy2 import gen_text_template, gen_all_questions, gen_answer_question_template

logging.basicConfig(level=logging.WARNING)
logger = init_logger(__name__)

cli = click.Group()

@cli.command(help="Extract biomedical entities from a given text.")
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
def extract_entities(text_file: str, output_file: str, model_name: str, metadata: str, review: bool = False):
    print("Extracting entities using the model %s..." % model_name)
    if metadata and os.path.exists(metadata):
        with open(metadata, "r") as f:
            metadata = f.read()
    else:
        metadata = {} # type: ignore

    with open(text_file, "r") as f:
        abstract = f.read()
        abstract = f"USER: {abstract} ASSISTANT: "

        if os.path.exists(output_file):
            if review:
                entities = json.load(open(output_file))

                if entities:
                    print(f"Entities found in the {text_file} file, so we will review them.")
                    print(f"Previous entities: {entities}\n")
                    abstract = f"""
{abstract}

The following entities are extracted by your previous run:
{entities}

Please carefully review the previously extracted results, following these steps:
1. Verify that each entity extracted aligns precisely with the designated categories. Ensure that the categorization is strict and appropriate.
2. Confirm that all entities listed under each category accurately match the category's criteria.
3. Assess the confidence scores assigned to each extraction. Consider the accuracy and relevance of the entity to its category, adjusting the scores to more accurately reflect the confidence level.
4. If you identify any discrepancies, inaccuracies, or misalignments with the categories, please correct them. Use the same format as the original extraction to present your corrections.

Your review should be thorough, ensuring the final extraction results are both accurate and logically structured according to the outlined categories.
"""
            else:
                print(f"Entities found in the {text_file} file, so we will skip the extraction.")
                return

        entities = extract_concepts(abstract, model=model_name, metadata=metadata)

    if entities:
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
def extract_relationships_1(text_file: str, model_name: str, metadata: str, output_file: str):
    if metadata and os.path.exists(metadata):
        with open(metadata, "r") as f:
            metadata = f.read()
    else:
        metadata = {} # type: ignore

    with open(text_file, "r") as f:
        text = f.read()
        relations = graph_prompt(text, model=model_name, metadata=metadata)

    if relations:
        with open(output_file, "w") as f:
            relations_str = json.dumps(relations, indent=4)
            f.write(relations_str)
    else:
        print(f"No relations found for the {text_file} file.")


# @cli.command(
#     help="Extract relationships between biomedical entities from a given abstract using strategy 2."
# )
# @click.option(
#     "--abstract-file",
#     "-a",
#     help="Abstract file which contains a paragraph.",
#     required=True,
#     type=click.Path(exists=True, file_okay=True, dir_okay=False),
# )
# @click.option(
#     "--input-file",
#     "-i",
#     help="Input file which contains a list of biomedical entities.",
#     required=True,
#     type=click.Path(exists=True, file_okay=True, dir_okay=False),
# )
# def extract_relationships_2(input_file: str, abstract_file: str):
#     with open(input_file, "r") as f:
#         items = f.readlines()

#     with open(abstract_file, "r") as f:
#         abstract = f.read()

#     items = list(
#         filter(lambda x: len(x) > 0, [item.strip() for item in items])
#     )  # remove empty lines and strip the spaces

#     valid_items = filter(
#         lambda x: len(x) > 0, get_valid_entities(items, topk=1, min_score=0.8)
#     )

#     print("Valid items: %s\n\n" % get_valid_entities(items, topk=5, min_score=0.5))

#     all_possible_items = [i[0].raw_name for i in valid_items]
#     print("All possible items: %s\n\n" % all_possible_items)
#     questions = gen_all_questions(all_possible_items)
#     print(gen_answer_question_template(questions, abstract))


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
def classify_text(input_file: str, output_file: str, model_name: str):
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
            outputs.append(classify(text, model=model_name))

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


if __name__ == "__main__":
    # Add the directory which contains this file to the python path
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    cli()
