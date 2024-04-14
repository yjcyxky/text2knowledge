import scipdf
import json
import pathlib
import os
from typing import Union


def list_pdfs(path):
    """List all pdfs in a directory"""
    pdfs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pdf"):
                pdfs.append(os.path.join(root, file))
    return pdfs


def gen_dest_path(pdf_file, output_dir):
    basename = pathlib.Path(pdf_file).stem
    output_path = os.path.join(output_dir, basename)
    return output_path, basename


def extract_fulltext(
    pdf_file, output_dir, grobid_url="https://kermitt2-grobid.hf.space"
) -> Union[None, str]:
    output_path, basename = gen_dest_path(pdf_file, output_dir)
    output_file = os.path.join(output_path, basename + ".json")
    os.makedirs(output_path, exist_ok=True)
    if os.path.exists(output_file):
        print("Output file (%s) already exists. Skipping..." % output_file)
        return None
    else:
        try:
            article_dict = scipdf.parse_pdf_to_dict(pdf_file, grobid_url=grobid_url)
            with open(output_file, "w") as f:
                json.dump(article_dict, f, indent=4)
            return output_file
        except Exception as e:
            print("Error processing %s: %s" % (pdf_file, e))
            return None


def extract_figures(pdf_file, output_dir):
    """Extract figures from pdfs"""
    output_path, basename = gen_dest_path(pdf_file, output_dir)
    datafile = os.path.join(output_path, "data", basename + ".json")
    pdf_dir = os.path.join(output_path, "pdf")
    new_pdf_file = os.path.join(pdf_dir, basename + ".pdf")
    if os.path.exists(output_path) and os.path.exists(new_pdf_file):
        print("Output folder (%s) already exists. Skipping..." % output_path)
    else:
        os.makedirs(pdf_dir, exist_ok=True)
        # Copy pdf to output folder
        os.system("cp '%s' '%s'" % (pdf_file, pdf_dir))

    if os.path.exists(datafile):
        print("Data file (%s) already exists. Skipping..." % datafile)
    else:
        print("Extracting figures from %s to %s..." % (pdf_dir, output_path))
        scipdf.parse_figures(pdf_dir, output_folder=output_path)
