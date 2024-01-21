from dataclasses import dataclass
from typing import List

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
