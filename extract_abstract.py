import json
import click

def extract(input_file: str, output_dir: str):
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract all abstracts from the JSON data
    abstracts = [entry['data'].get('abstract') for entry in data]
    pmids = [entry['data'].get('pmid') for entry in data]

    for pmid, abstract in zip(pmids, abstracts):
        if abstract and not pmid:
            print(f'PMID: {pmid}\nAbstract: {abstract}\n')

        if abstract and pmid:
            with open(f'{output_dir}/{pmid}.txt', 'w') as file:
                file.write(abstract)

@click.command(help="Extract abstracts from the JSON data which are exported from the prophet-studio service.")
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
def main(input_file, output_dir):
    extract(input_file, output_dir)


if __name__ == '__main__':
    main()