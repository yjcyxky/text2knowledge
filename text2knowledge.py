import click
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from text2knowledge.utils import Score, batch_similarity, get_topk_items, load_model, load_tokenizer, gen_word_embedding, get_valid_entities
from text2knowledge.pdf import list_pdfs, extract_fulltext, extract_figures


def gen_text_template(input_text: str) -> str:
    return f"""Find all biomedical items from the following text:

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

    print("Valid items: %s\n\n" % get_valid_entities(items, topk=5, min_score=0.5))

    all_possible_items = [i[0].raw_name for i in valid_items]
    print("All possible items: %s\n\n" % all_possible_items)
    questions = gen_all_questions(all_possible_items)
    print(gen_answer_question_template(questions, abstract))

@click.command(help="Extract figures and fulltext from pdfs.")
@click.option("--pdf-dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), help="Directory of pdfs.")
@click.option("--pdf-file", type=click.Path(exists=True, file_okay=True, dir_okay=False), help="Path to pdf file.")
@click.option("--output-dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), help="Output directory.")
@click.option("--grobid-url", default="http://192.168.0.123:8070", help="URL of grobid service, default: http://192.168.0.123:8070")
def pdf2text(pdf_dir, pdf_file, output_dir, grobid_url):
    if pdf_dir and os.path.isdir(pdf_dir):
        pdfs = list_pdfs(pdf_dir)
    elif pdf_file and os.path.isfile(pdf_file):
        pdfs = [pdf_file]
    else:
        raise ValueError("Please specify either pdf-dir or pdf-file")

    for pdf in pdfs:
        print("Processing %s..." % pdf)
        print("Extract fulltext...")

        # External service: https://kermitt2-grobid.hf.space
        extract_fulltext(pdf, output_dir, grobid_url=grobid_url)
        time.sleep(5)

        print("Extract figures...")
        extract_figures(pdf, output_dir)

        print("Done!\n\n")


if __name__ == "__main__":
    cli()
