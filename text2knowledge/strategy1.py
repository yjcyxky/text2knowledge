import re
import json
import logging
import text2knowledge.ollama.client as client
from text2knowledge.prompt_template import (
    ENTITY_EXTRACTION_PROMPT_TEMPLATE,
    RELATION_EXTRACTION_PROMPT_TEMPLATE,
    CLASSIFICATION_PROMPT_TEMPLATE,
)
from text2knowledge.utils import init_logger

logger = init_logger(__name__)


def extract_json(text: str) -> dict | None:
    # Using a regular expression to extract JSON strings from the provided text
    json_pattern = re.compile(r"\{.*?\}", re.DOTALL)
    matches = json_pattern.findall(text)

    if matches:
        # Try to load the first JSON string found in the text
        try:
            json_data = json.loads(matches[0])
            return json_data
        except json.JSONDecodeError:
            return None
    else:
        return None


def extract_entities(
    prompt: str,
    metadata={},
    model="mistral-openorca:latest",
    use_system=False,
    options={},
):
    if use_system:
        response, _ = client.generate(
            model_name=model,
            system=ENTITY_EXTRACTION_PROMPT_TEMPLATE,
            prompt=prompt,
            options=options,
        )
    else:
        prompt = f"{ENTITY_EXTRACTION_PROMPT_TEMPLATE}\n\n{prompt}"
        response, _ = client.generate(model_name=model, prompt=prompt, options=options)

    try:
        data = extract_json(str(response))
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return [dict(item, **metadata) for item in data]
    except:
        msg = f"ERROR ### Here is the buggy response: {response}"
        logger.info(msg)
        return {
            "error": msg,
            "metadata": metadata
        }


def extract_relations(input: str, metadata={}, model="mistral-openorca:latest", use_system=False, options={}):
    if model == None:
        model = "mistral-openorca:latest"

    if use_system:
        USER_PROMPT = f"context: ```{input}``` \n\n output: "
        response, _ = client.generate(model_name=model, system=RELATION_EXTRACTION_PROMPT_TEMPLATE, prompt=USER_PROMPT, options=options)
    else:
        PROMPT = f"{RELATION_EXTRACTION_PROMPT_TEMPLATE}\n\n{input}"
        response, _ = client.generate(model_name=model, prompt=PROMPT, options=options)

    try:
        data = extract_json(str(response))
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return [dict(item, **metadata) for item in data]
    except:
        msg = f"ERROR ### Here is the buggy response: {response}"
        logger.warning(msg)
        return {
            "error": msg,
            "metadata": metadata
        }


def classify_article(input: str, model="mistral-openorca:latest", use_system=False, options={}):
    if model == None:
        model = "mistral-openorca:latest"

    if use_system:
        input = f"```{input}```"
        response, _ = client.generate(
            model_name=model,
            system=CLASSIFICATION_PROMPT_TEMPLATE,
            prompt=input,
            options=options,
        )
    else:
        input = f'{CLASSIFICATION_PROMPT_TEMPLATE}\n```{input}```'
        response, _ = client.generate(model_name=model, prompt=input, options=options)

    logger.debug(f"{input}\n")
    title = input.split("\n")[0].strip()
    abstract = input.split("\n")[1].strip()

    try:
        data = extract_json(str(response))
        if data is None:
            raise Exception("The response is not a JSON object.")
        else:
            return {
                "category": data["category"],
                "title": title,
                "abstract": abstract,
                "reason": data["reason"],
                "response": response,
            }
    except Exception as e:
        msg = f"\n\nERROR ### Here is the buggy response: {response}"
        logger.info(msg)

        return {
            "error": msg,
            "category": "Unknown",
            "title": title,
            "abstract": abstract,
        }
