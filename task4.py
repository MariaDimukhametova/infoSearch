import math
import json
import pymorphy2
import zipfile
import re
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

parser = 'html.parser'
morph = pymorphy2.MorphAnalyzer()
file_path = "download.zip"
index_file = 'inverted_index.json'
tokens_tfidf_dir = 'tokens_tfidf/'
lemmas_tfidf_dir = 'lemmas_tfidf/'


def process_tokens(tokens):
    return set(token.lower() for token in tokens
               if token.lower() not in stopwords.words("russian")
               and re.compile("^[а-яё]+$").match(token.lower()))


def process_tokens_list(tokens):
    return [token.lower() for token in tokens
            if token.lower() not in stopwords.words("russian")
            and re.compile("^[а-яё]+$").match(token.lower())]


def tokenize_text(text):
    tokens = word_tokenize(text.replace('.', ' '))
    return process_tokens(tokens)


def build_index_tokens(zip_f):
    index = {}

    for i, f in enumerate(zip_f.filelist):
        content = zip_f.open(f)
        text = BeautifulSoup(content, parser).get_text()
        tokens = tokenize_text(text)
        for token in tokens:
            index.setdefault(token, set()).add(i)

    return index


def index_to_json(filename, ind):
    ind_json = {key: list(value) for key, value in ind.items()}
    with open(filename, "w", encoding='utf-8') as inverted_index_file:
        json.dump(ind_json, inverted_index_file, ensure_ascii=False, indent=4)


def calculate_tf(q, tokens):
    return tokens.count(q) / float(len(tokens))


def calculate_idf(q, index, docs_count=100):
    return math.log(docs_count / float(len(index[q])))


def word_to_lemma(word):
    return morph.parse(word)[0].normal_form


def calculate_tfidf(zip_f, lemmas_index, tokens_index):
    for f in zip_f.filelist:
        content = zip_f.open(f)
        text = BeautifulSoup(content, parser).get_text()

        tokens = process_tokens_list(word_tokenize(text.replace('.', ' ')))
        lemmas = [word_to_lemma(token) for token in tokens]

        res_tokens = []
        for token in set(tokens):
            if token in tokens_index:
                tf = calculate_tf(token, tokens)
                idf = calculate_idf(token, tokens_index)
                res_tokens.append(f"{token} {idf} {tf * idf}")

        with open(f"{tokens_tfidf_dir}{f.filename}.txt", "w", encoding='utf-8') as token_f:
            token_f.write("\n".join(res_tokens))

        res_lemmas = []
        for lemma in set(lemmas):
            if lemma in lemmas_index:
                tf = calculate_tf(lemma, lemmas)
                idf = calculate_idf(lemma, lemmas_index)
                res_lemmas.append(f"{lemma} {idf} {tf * idf}")

        with open(f"{lemmas_tfidf_dir}{f.filename}.txt", "w", encoding='utf-8') as lemma_f:
            lemma_f.write("\n".join(res_lemmas))


if __name__ == '__main__':
    zip_file = zipfile.ZipFile(file_path, "r")

    inverted_index_tokens = build_index_tokens(zip_file)
    index_to_json(index_file, inverted_index_tokens)

    with open(index_file, 'r', encoding='utf-8') as file:
        inverted_index = json.load(file)

    calculate_tfidf(zip_file, inverted_index, inverted_index)
