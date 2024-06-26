import json
import math
import os
from typing import Dict, List
from nltk import word_tokenize

LEMMAS_TFIDF = 'lemmas_tfidf'
LEMMAS_TFIDF_PATH = 'lemmas_tfidf/'
LEMMA_TOKENS_FILE = 'lemmas.txt'
INVERTED_INDEX_FILE = 'inverted_index.json'


def load_inverted_index():
    try:
        with open(INVERTED_INDEX_FILE, encoding='utf-8') as file:
            json_index = file.read()
            index = json.loads(json_index)
            return index
    except FileNotFoundError:
        print(f"Файл {INVERTED_INDEX_FILE} не найден.")
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании файла JSON: {e}")


def load_lemma_tokens() -> Dict[str, str]:
    lemmas = {}
    with open(LEMMA_TOKENS_FILE, encoding='utf-8') as lemma_file:
        lines = lemma_file.readlines()
        for line in lines:
            line = line.rstrip('\n')
            words = line.split(' ')
            for word in words:
                lemmas[word] = words[0]
    return lemmas


def load_doc_to_lemma_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF_PATH):
        with open(os.path.join(LEMMAS_TFIDF_PATH, file_name), encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            result[file_name] = {data[0]: float(data[2]) for data in [line.rstrip('\n').split(' ') for line in lines]}
    return result


def load_lemma_to_doc_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF_PATH):
        with open(os.path.join(LEMMAS_TFIDF_PATH, file_name), encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            for line in lines:
                data = line.rstrip('\n').split(' ')
                lemma_to_docs_tf_idf = result.get(data[0], {})
                lemma_to_docs_tf_idf[file_name[:-4]] = float(data[2])
                result[data[0]] = lemma_to_docs_tf_idf
    return result


def calculate_doc_vector_length(doc_to_words: Dict[str, float]):
    return math.sqrt(sum(i ** 2 for i in doc_to_words.values()))


def multiply_vectors(query_vector: List[str], doc_vector: Dict[str, float], doc_vector_len: float):
    return sum(doc_vector.get(token, 0) for token in query_vector) / len(query_vector) / doc_vector_len


def merge_or(set1, set2):
    return set1.union(set2)


def process_query(query: str):
    tokens = word_tokenize(query, language='russian')
    lemmas = [token_to_lemma.get(token, token) for token in tokens]
    doc_set = set()
    for lemma in lemmas:
        doc_set = merge_or(doc_set, reverse_index.get(lemma, set()))
    results = {doc: multiply_vectors(lemmas, doc_to_lemma.get(doc, {}), doc_lengths.get(doc, 0.0001)) for doc in doc_set}
    return dict(sorted(results.items(), key=lambda r: r[1], reverse=True))


docs_list = os.listdir(LEMMAS_TFIDF_PATH)
doc_to_lemma = load_doc_to_lemma_tf_idf()
lemma_to_doc = load_lemma_to_doc_tf_idf()
doc_lengths = {doc: calculate_doc_vector_length(doc_to_lemma[doc]) for doc in docs_list}
token_to_lemma = load_lemma_tokens()
reverse_index = load_inverted_index()


if __name__ == '__main__':

    while True:
        user_input = input("Введите запрос:\n")
        if user_input.lower() == 'exit':
            exit()
        try:
            print(process_query(user_input))
        except Exception as e:
            print(f"Произошла ошибка: {e.with_traceback()}. Попробуйте снова")
