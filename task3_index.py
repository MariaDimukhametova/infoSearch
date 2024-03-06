import json
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup

data_dir = 'data/'
tokens_file = 'tokens.txt'
index_file = 'inverted_index.json'


def read_file(file_path):
    with open(file_path, encoding='utf-8') as file:
        return file.read()


def json_to_file(data, file_path):
    with open(file_path, 'w+', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def build_index():
    filenames = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and f.endswith('.html')]
    filenames.sort(key=lambda x: int(x.replace('.html', '')))

    tokens = read_file(tokens_file).splitlines()

    inverted_index = {}

    for i, filename in enumerate(filenames):
        content = read_file(join(data_dir, filename))
        text = BeautifulSoup(content, 'html.parser').get_text().lower()

        for token in tokens:
            if token in text:
                inverted_index.setdefault(token, set()).add(filename)

    inverted_index = {key: list(value) for key, value in inverted_index.items()}
    json_to_file(inverted_index, index_file)


if __name__ == "__main__":
    build_index()
