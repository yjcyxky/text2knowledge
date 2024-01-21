import json
import text2knowledge.ollama.client as client
from text2knowledge.prompt_template import ENTITY_EXTRACTION_PROMPT_TEMPLATE, RELATION_EXTRACTION_PROMPT_TEMPLATE


def extract_concepts(prompt: str, metadata={}, model="mistral-openorca:latest"):
    response, _ = client.generate(model_name=model, system=ENTITY_EXTRACTION_PROMPT_TEMPLATE, prompt=prompt)
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

    USER_PROMPT = f"context: ```{input}``` \n\n output: "
    response, _ = client.generate(model_name=model, system=RELATION_EXTRACTION_PROMPT_TEMPLATE, prompt=USER_PROMPT)
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result
