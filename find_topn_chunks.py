from text2knowledge.utils import find_topn_text_chunks
import click
import os
import pandas as pd


@click.command(help="Find top N text chunks from a given text.")
@click.option(
    "--question",
    "-q",
    help="Question.",
    required=True,
    type=str,
)
@click.option(
    "--text-chunks",
    "-t",
    help="A file containing text chunks. It should be a json file with the following columns: text, name, label.",
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
    "--topn",
    "-n",
    help="Top N text chunks.",
    required=True,
    type=int,
)
@click.option(
    "--min-score",
    "-s",
    help="Minimum score for the text chunks.",
    required=False,
    default=0.0,
    type=float,
)
@click.option(
    "--model-name",
    "-m",
    help="Model name.",
    required=True,
    type=str,
)
@click.option(
    "--use-cohere",
    "-c",
    help="Use cohere.",
    required=False,
    default=False,
    type=bool,
    is_flag=True,
)
@click.option(
    "--pdf-dir",
    "-p",
    help="PDF directory.",
    required=False,
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def find_topn_chunks(
    question: str,
    text_chunks: str,
    output_file: str,
    topn: int,
    model_name: str,
    min_score: float = 0.0,
    use_cohere: bool = False,
    pdf_dir: str | None = None,
):
    print("Finding top N text chunks...")
    results = find_topn_text_chunks(
        question, text_chunks, model_name=model_name, topn=topn, min_score=min_score, use_cohere=use_cohere, use_vectorized=True
    )
    results = pd.DataFrame(results)
    results.sort_values(by="score", ascending=False, inplace=True)

    if len(results) == 0:
        print("No text chunks found.")
        return
    else:
        results["target_text"] = results["target_text"].apply(lambda x: x.replace("\n", "\\n"))
        results.to_csv(output_file, sep="\t", index=False, quoting=1, quotechar='"')
        print(f"Top {topn} text chunks are saved in the {output_file} file.")

        if pdf_dir is None:
            return

        which_papers = results["filename"].unique()
        topn_papers_dir = os.path.join(os.path.dirname(output_file), "topn_papers")
        if os.path.exists(topn_papers_dir):
            raise FileExistsError(f"{topn_papers_dir} already exists.")

        os.makedirs(topn_papers_dir, exist_ok=True)
        for paper in which_papers:
            paper_pdf = os.path.basename(paper.replace(".json", ".pdf"))
            paper_pdf = os.path.join(pdf_dir, paper_pdf)
            if not os.path.exists(paper_pdf):
                print(f"{paper_pdf} does not exist.")
                continue
            else:
                os.system(f"cp -f '{paper_pdf}' {topn_papers_dir}")


if __name__ == "__main__":
    find_topn_chunks()
