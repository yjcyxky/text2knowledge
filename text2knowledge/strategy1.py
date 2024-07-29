import re
import json
import logging
import pandas as pd
import torch
import text2knowledge.ollama.client as client
from text2knowledge.prompt_template import (
    make_entity_extraction_prompt,
    make_relation_extraction_prompt,
    make_classification_prompt,
    make_entity_extraction_review_prompt,
)
from text2knowledge.utils import init_logger, EmbeddingGenerator

logger = init_logger(__name__)


def get_mapped_entities(
    entities: list, embeddings: pd.DataFrame, model_name: str
) -> list:
    embedding_lst = embeddings["embedding"].tolist()
    embedding_tensor_lst = [torch.tensor(embedding) for embedding in embedding_lst]
    mapped_entities = []
    all_labels = embeddings["label"].tolist()

    for entity in entities:
        category = entity.get("category", "")
        entity_name = entity.get("concept", "")
        embedding_generator = EmbeddingGenerator(model_name)
        entity_name_embedding = embedding_generator.gen_text_embedding(entity_name)

        scores = embedding_generator.vectorized_similarity(
            entity_name_embedding, embedding_tensor_lst
        )
        index_scores = list(enumerate(scores))
        index_scores.sort(key=lambda x: x[1], reverse=True)

        # TODO: How to use the category information to filter the potential references?
        top_5_index_scores = index_scores[:5]
        top_5_indexes = [index for index, _ in top_5_index_scores]
        mapped_entities = embeddings.iloc[top_5_indexes].to_dict(orient="records")
        mapped_entities_with_scores = []
        for i, entity in enumerate(mapped_entities):
            entity["score"] = top_5_index_scores[i][1]
            mapped_entities_with_scores.append(entity)

        entity["potential_references"] = mapped_entities_with_scores

        mapped_entities.append(entity)

    return mapped_entities


def extract_json(text: str, is_list: bool = False) -> dict | list | None:
    # Using a regular expression to extract JSON objects or arrays from the provided text
    pattern = r"\{.*?\}" if not is_list else r"\[[\n ]+\{.*?\}[\n ]+\]"
    json_pattern = re.compile(pattern, re.DOTALL)
    matches = json_pattern.findall(text)

    for match in matches:
        try:
            num_single_quotes = match.count("'")
            num_double_quotes = match.count('"')

            if num_single_quotes > num_double_quotes:
                cleaned_match = match.replace('"', "`")
                cleaned_match = cleaned_match.replace("'", '"')
            else:
                cleaned_match = match.replace("'", "`")

            json_data = json.loads(cleaned_match)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            continue

    return None


def correct_extracted_entities(
    text: str,
    metadata={},
    model="mistral-openorca:latest",
    options={},
    is_list=False,
    entities=[],
):
    prompt = make_entity_extraction_review_prompt(text, entities)
    response, _ = client.generate(model_name=model, prompt=prompt, options=options)

    try:
        data = extract_json(str(response), is_list=is_list)
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return {
                "entities": data,
                "metadata": metadata,
                "response": response,
            }
    except:
        msg = f"ERROR ### Here is the buggy response: {response}"
        logger.info(msg)
        return {
            "response": msg,
            "metadata": metadata,
            "entities": [],
            "error": True,
        }


def extract_entities(
    text: str,
    metadata={},
    model="mistral-openorca:latest",
    use_system=False,
    options={},
    embeddings: pd.DataFrame | None = None,
    embedding_model_name: str = "mistralai/Mistral-7B-v0.1",
):
    if use_system:
        response, _ = client.generate(
            model_name=model,
            system=make_entity_extraction_prompt(None),
            prompt=text,
            options=options,
        )
    else:
        prompt = make_entity_extraction_prompt(text)
        response, _ = client.generate(model_name=model, prompt=prompt, options=options)

    try:
        data = extract_json(str(response), is_list=True)
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return {
                # entities_with_potential_references or entities_without_potential_references
                "entities": (
                    # TODO: Pick up a better model for the embeddings
                    get_mapped_entities(data, embeddings, embedding_model_name)  # type: ignore
                    if embeddings is not None
                    else data
                ),
                "metadata": metadata,
                "response": response,
                "text": text,
                "prompt": prompt,
            }
    except:
        msg = f"ERROR ### Here is the buggy response: {response}"
        logger.info(msg)
        return {
            "response": msg,
            "metadata": metadata,
            "entities": [],
            "text": text,
            "prompt": prompt,
            "error": True,
        }


def extract_relations(
    text: str,
    metadata={},
    model="mistral-openorca:latest",
    use_system=False,
    options={},
):
    if model == None:
        model = "mistral-openorca:latest"

    if use_system:
        response, _ = client.generate(
            model_name=model,
            system=make_relation_extraction_prompt(None),
            prompt=text,
            options=options,
        )
    else:
        PROMPT = make_relation_extraction_prompt(text)
        response, _ = client.generate(model_name=model, prompt=PROMPT, options=options)

    try:
        data = extract_json(str(response), is_list=True)
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return {
                "relations": data,
                "metadata": metadata,
                "response": response,
                "text": text,
                "prompt": PROMPT,
            }
    except:
        msg = f"ERROR ### Here is the buggy response: {response}"
        logger.warning(msg)
        return {
            "error": True,
            "metadata": metadata,
            "relations": [],
            "text": text,
            "prompt": PROMPT,
            "response": response,
        }


def classify_article(
    text: str, model="mistral-openorca:latest", use_system=False, options={}
):
    if model == None:
        model = "mistral-openorca:latest"

    if use_system:
        response, _ = client.generate(
            model_name=model,
            system=make_classification_prompt(None),
            prompt=text,
            options=options,
        )
    else:
        prompt = make_classification_prompt(text)
        response, _ = client.generate(model_name=model, prompt=prompt, options=options)

    logger.debug(f"{input}\n")

    try:
        data = extract_json(str(response))
        # We assume that the data is a dictionary.
        if data is None or type(data) != dict:
            raise Exception("The response is not a JSON object.")
        else:
            return {
                "category": data.get("category", ""),
                "text": text,
                "reason": data.get("reason", ""),
                "response": response,
                "prompt": prompt,
            }
    except Exception as e:
        msg = f"\n\nERROR ### Here is the buggy response: {response}"
        logger.info(msg)

        return {
            "response": msg,
            "category": "Unknown",
            "text": text,
            "prompt": prompt,
            "error": True,
        }
