import os
import time
import spacy
import pandas as pd
import json
import click
from text2knowledge.pdf import list_pdfs, extract_fulltext, extract_figures

cli = click.Group()


def extract_abstract(input_file: str, output_dir: str):
    with open(input_file, "r") as file:
        data = json.load(file)

    # Extract all abstracts from the JSON data
    abstracts = [entry["data"].get("abstract") for entry in data]
    pmids = [entry["data"].get("pmid") for entry in data]

    for pmid, abstract in zip(pmids, abstracts):
        if abstract and not pmid:
            print(f"PMID: {pmid}\nAbstract: {abstract}\n")

        if abstract and pmid:
            with open(f"{output_dir}/{pmid}.txt", "w") as file:
                file.write(abstract)


def extract_sentences(input_dir: str, output_file: str, sentence_size: int):
    print(f"Extracting sentences with size {sentence_size}...")
    pmids = os.listdir(input_dir)
    text_chunks = []
    nlp = spacy.load("en_core_web_sm")

    files = []
    for pmid in pmids:
        files.append(f"{input_dir}/{pmid}/{pmid}.json")

    for file in files:
        filename = os.path.basename(file)
        pmid = os.path.basename(file).replace(".json", "")
        if not os.path.exists(file):
            continue

        with open(file, "r") as f:
            data = json.load(f)

        sections = data.get("sections")
        text = [section.get('text') for section in sections]
        full_text = " ".join(text)

        print("Use spacy to split the %s into sentences..." % pmid)
        doc = nlp(full_text)
        sentences = [sent.text for sent in doc.sents]
        merged_sentences = []
        for i in range(0, len(sentences), sentence_size):
            merged_sentences.append("".join(sentences[i:i + sentence_size]))

        for idx, sentence in enumerate(merged_sentences):
            text_chunks.append(
                {
                    "text": sentence,
                    "name": f"{pmid}-{idx}",
                    "label": "pubtext",
                    "pmid": pmid,
                    "filename": filename,
                }
            )

    print(f"Saving sentences to {output_file}...")
    df = pd.DataFrame(text_chunks)
    df.to_json(output_file, orient="records", lines=False, force_ascii=False)


def extract_chunks(input_dir: str, output_file: str, chunk_size: int):
    pmids = os.listdir(input_dir)
    text_chunks = []

    files = []
    for pmid in pmids:
        files.append(f"{input_dir}/{pmid}/{pmid}.json")

    for file in files:
        filename = os.path.basename(file)
        pmid = os.path.basename(file).split(".")[0]
        if not os.path.exists(file):
            continue

        with open(file, "r") as f:
            data = json.load(f)

        sections = data.get("sections")
        text = [section.get('text') for section in sections]
        full_text = " ".join(text)
        chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

        for i, chunk in enumerate(chunks):
            text_chunks.append(
                {
                    "text": chunk,
                    "name": f"{pmid}-{i}",
                    "label": "pubtext",
                    "pmid": pmid,
                    "filename": filename,
                }
            )

    df = pd.DataFrame(text_chunks)
    df.to_json(output_file, orient="records", lines=False, force_ascii=False)


def extract_sections(input_dir: str, output_file: str):
    pmids = os.listdir(input_dir)
    text_chunks = []

    files = []
    for pmid in pmids:
        files.append(f"{input_dir}/{pmid}/{pmid}.json")

    for file in files:
        filename = os.path.basename(file)
        pmid = os.path.basename(file).split(".")[0]
        if not os.path.exists(file):
            continue

        with open(file, "r") as f:
            data = json.load(f)

        sections = data.get("sections")
        for section in sections:
            text_chunks.append(
                {
                    "text": section.get("text"),
                    "name": f"{pmid}-{section.get('heading')}",
                    "label": "pubtext",
                    "pmid": pmid,
                    "filename": filename,
                }
            )

    df = pd.DataFrame(text_chunks)
    df.to_json(output_file, orient="records", lines=False, force_ascii=False)


@cli.command(
    help="Extract abstracts from the JSON data which are exported from the prophet-studio service."
)
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
def abstract(input_file, output_dir):
    extract_abstract(input_file, output_dir)


@cli.command(
    help="Extract text chunks from the JSON data which are exported from the prophet-studio service."
)
@click.argument("input_dir", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--chunk-type", default="sections", help="Chunk type.", type=click.Choice(["sections", "chunks", "sentences"]))
@click.option("--chunk-size", default=1000, help="Chunk size, only used when chunk-type is chunks.", type=int)
@click.option("--sentence-size", default=5, help="Sentence size, only used when chunk-type is sentences.", type=int)
def text_chunks(input_dir, output_file, chunk_type, chunk_size, sentence_size):
    if chunk_type == "sections":
        print("Extracting sections...")
        extract_sections(input_dir, output_file)
    elif chunk_type == "chunks":
        print(f"Extracting chunks with size {chunk_size}...")
        extract_chunks(input_dir, output_file, chunk_size)
    elif chunk_type == "sentences":
        print(f"Extracting sentences with size {sentence_size}...")
        extract_sentences(input_dir, output_file, sentence_size)


@cli.command(help="Extract figures and fulltext from pdfs.")
@click.option(
    "--pdf-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory of pdfs, you can specify either pdf-dir or pdf-file.",
)
@click.option(
    "--pdf-file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to pdf file, you can specify either pdf-dir or pdf-file.",
)
@click.option(
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Output directory.",
)
@click.option(
    "--grobid-url",
    default="http://192.168.0.123:8070",
    help="URL of grobid service, you can launch a local grobid server, such as http://0.0.0.0:8070. Or you can use the public service: https://kermitt2-grobid.hf.space",
)
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
        r = extract_fulltext(pdf, output_dir, grobid_url=grobid_url)
        # if r is not None:
        print("Extract figures...")
        extract_figures(pdf, output_dir)
        # time.sleep(5)

        print("Done!\n\n")


cli.add_command(abstract)

if __name__ == "__main__":
    cli()
