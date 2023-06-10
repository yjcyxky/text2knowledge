import os
import click
import pickle
import pandas as pd
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

model = SentenceTransformer("all-mpnet-base-v2")


def similarity(query, passage_embeddings):
    query_embedding = model.encode(query)

    results = util.dot_score(query_embedding, passage_embeddings)  # type: ignore

    return results.tolist()[0]


@dataclass
class Score:
    score: float
    category: str
    name: str
    raw_name: str


def batch_similarity(
    query_item: str, passage_embeddings_dict, metadata: Dict[str, pd.DataFrame]
) -> List[Score]:
    all_results: List[Score] = []
    for category, passage_embeddings in passage_embeddings_dict.items():
        results = similarity(query_item, passage_embeddings)
        m = metadata.get(category, pd.DataFrame())
        for i, result in enumerate(results):
            r = Score(
                score=result,
                category=category,
                name=m.iloc[i]["name"],
                raw_name=query_item,
            )
            all_results.append(r)

            # print("Batch similarity done. %s, %s" % (query_item, r))

    return all_results


def get_topk_items(
    results: List[Score], k: int = 3, min_score: float = 0.5
) -> List[Score]:
    results.sort(key=lambda x: x.score, reverse=True)
    results = [r for r in results if r.score > min_score]
    return results[:k]


def read_ontology(filepath) -> pd.DataFrame:
    ontology = pd.read_csv(filepath, delimiter=",")
    return ontology


def get_valid_entities(
    items: List[str], topk: int = 3, min_score: float = 0.5
) -> List[List[Score]]:
    filepath = "data/embeddings.pickle"

    ontology_files = [
        os.path.join("data", file)
        for file in os.listdir("data")
        if file.endswith(".csv")
    ]

    ontology_metadata = {}
    ontology_items = {}
    for file in ontology_files:
        ontology = read_ontology(file)
        filename = os.path.splitext(os.path.basename(file))[0]
        ontology_metadata[filename] = ontology
        ontology_items[filename] = ontology["name"].tolist()
        print("Load %s ontology items: %s" % (filename, len(ontology_items[filename])))

    if os.path.exists(filepath):
        with open(filepath, "rb") as handle:
            passage_embeddings = pickle.load(handle)
    else:
        passage_embeddings = {}
        for category, ontology_item_lst in ontology_items.items():
            # if category in [
            #     "chemical",
            #     "anatomy",
            #     "biological_process",
            #     "cellular_component",
            #     "molecular_function",
            #     "gene",
            # ]:
            #     continue

            print("Encode %s items" % category)
            passage_embeddings[category] = model.encode(
                ontology_item_lst, show_progress_bar=True
            )

        with open(filepath, "wb") as handle:
            pickle.dump(passage_embeddings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Load passage embeddings...")
    final_results: List[List[Score]] = []
    for item in items:
        results = batch_similarity(item, passage_embeddings, ontology_metadata)

        final_results.append(get_topk_items(results, topk, min_score=min_score))

    return final_results


def gen_text_template(input_text: str) -> str:
    return f"""Find all biomedical items in the following text:

{input_text}
"""


@dataclass
class Question:
    question: str
    answer: str


def gen_question_template(source_item: str, target_item: str) -> str:
    return f"""Is there any relationship between "{source_item}" and "{target_item}"?"""


answers = [
    "A. associated_with",
    "B. upregulated_in",
    "C. downregulated_in",
    "D. activated_by",
    "E. inhibited_by",
    "F. reduced_by",
    "G. increased_by",
    "H. alleviated_by",
    "I. induced_by",
    "J. No relationship",
]


# Pick up two items by random from the list of items and generate all possible questions, but the order of the items is no matter here.
def gen_all_questions(items: List[str]) -> List[Question]:
    questions = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            source_item = items[i]
            target_item = items[j]
            questions.append(
                Question(
                    question=gen_question_template(source_item, target_item),
                    answer="\n".join(answers),
                )
            )
    return questions


def gen_answer_question_template(questions: List[Question], input_text: str) -> str:
    formatted_questions = [
        f"{i+1}. {q.question}\n{q.answer}" for i, q in enumerate(questions)
    ]
    formatted_question_str = "\n\n".join(formatted_questions)
    return f"""Please use the following text as the context information and answer the questions step by step:

{input_text}

{formatted_question_str}
"""


cli = click.Group()


@cli.command(help="Generate prompt text for finding biomedical entities.")
@click.option(
    "--abstract-file",
    "-i",
    help="Abstract file.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
def find_entity(abstract_file: str):
    with open(abstract_file, "r") as f:
        abstract = f.read()
        print(gen_text_template(abstract))


@cli.command(
    help="Generate prompt text for finding relationships between biomedical entities."
)
@click.option(
    "--abstract-file",
    "-a",
    help="Abstract file which contains a paragraph.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--input-file",
    "-i",
    help="Input file which contains a list of biomedical entities.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
def find_relationship(input_file: str, abstract_file: str):
    with open(input_file, "r") as f:
        items = f.readlines()

    with open(abstract_file, "r") as f:
        abstract = f.read()

    items = list(
        filter(lambda x: len(x) > 0, [item.strip() for item in items])
    )  # remove empty lines and strip the spaces

    valid_items = filter(
        lambda x: len(x) > 0, get_valid_entities(items, topk=1, min_score=0.8)
    )

    all_possible_items = [i[0].raw_name for i in valid_items]
    print("All possible items: %s\n\n" % all_possible_items)
    questions = gen_all_questions(all_possible_items)
    print(gen_answer_question_template(questions, abstract))


if __name__ == "__main__":
    cli()
