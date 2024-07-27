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

def extract_concepts(prompt: str, metadata={}, model="mistral-openorca:latest"):
    response, _ = client.generate(model_name=model, system=ENTITY_EXTRACTION_PROMPT_TEMPLATE, prompt=prompt)
    # prompt = f"{ENTITY_EXTRACTION_PROMPT_TEMPLATE}\n\n{prompt}"
    # response, _ = client.generate(model_name=model, prompt=prompt, options={
    #     "temperature": 0.6,
    # })
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        print("If you get `404 Client Error: Not Found`, please check if the model name is correct or you have installed the model. If you get `500 Server Error: Internal Server Error`, please check if the model is running.")
        result = None
    return result


def graph_prompt(input: str, metadata={}, model="mistral-openorca:latest"):
    if model == None:
        model = "mistral-openorca:latest"

    # model_info = client.show(model_name=model)
    # print( chalk.blue(model_info))

    # USER_PROMPT = f"context: ```{input}``` \n\n output: "
    # response, _ = client.generate(model_name=model, system=RELATION_EXTRACTION_PROMPT_TEMPLATE, prompt=USER_PROMPT)

    USER_PROMPT = f"context: ```{input}``` \n\n output: "
    response, _ = client.generate(
        model_name=model, prompt=USER_PROMPT, system=RELATION_EXTRACTION_PROMPT_TEMPLATE
    )
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result


def classify(input: str, model="mistral-openorca:latest") -> dict:
    if model == None:
        model = "mistral-openorca:latest"

    # input = f'{CLASSIFICATION_PROMPT_TEMPLATE}\n```{input}```'
    # response, _ = client.generate(model_name=model, prompt=input)
    logger.debug(f"{input}\n")
    response, _ = client.generate(model_name=model, prompt=f"```{input}```", system=CLASSIFICATION_PROMPT_TEMPLATE)

    title = input.split("\n")[0].strip()
    abstract = input.split("\n")[1].strip()

    try:
        data = json.loads(response)
        return {
            "category": data["category"],
            "title": title,
            "abstract": abstract,
            "reason": data["reason"],
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
