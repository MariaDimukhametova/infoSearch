import os
import re
import nltk
import ssl
import pymorphy2

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


def clean_token(token):
    return re.sub('[^а-яА-ЯёЁ]', '', token)


def extract_tokens(data, language='russian'):
    tokens = word_tokenize(data, language=language)
    filtered_tokens = set()
    stop_words = set(stopwords.words(language))

    for token in tokens:
        cleaned = clean_token(token)
        if cleaned and cleaned not in stop_words and len(cleaned) > 1:
            filtered_tokens.add(cleaned)

    return filtered_tokens


def process(tokens, output_file='tokens.txt', lemma_output_file='lemmas.txt'):
    analyzer = pymorphy2.MorphAnalyzer()
    lemmas = {}

    with open(output_file, 'w', encoding='utf-8') as tokens_file, open(lemma_output_file, 'w', encoding='utf-8') \
            as lemmas_file:
        for token in tokens:
            tokens_file.write(token + '\n')
            normal_form = analyzer.parse(token)[0].normal_form

            if normal_form not in lemmas:
                lemmas[normal_form] = []
            lemmas[normal_form].append(token)

        for lemma, tokens_list in lemmas.items():
            lemmas_file.write(f"{lemma}: {' '.join(tokens_list)}\n")


if __name__ == "__main__":
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    data = ''
    for article in os.listdir('data/'):
        with open(os.path.join('data', article), 'r', encoding='utf-8') as file:
            data += file.read().lower() + '\n'

    filtered_tokens = extract_tokens(data)
    process(filtered_tokens)
