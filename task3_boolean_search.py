import json
from collections import defaultdict
import pymorphy2

INDEX_PATH = "inverted_index.json"


def get_normal_form(word, morph):
    return morph.parse(word)[0].normal_form


def apply_operator(operator, result, operand, all_indexes):
    if operator == "&":
        return result.intersection(operand)
    elif operator == "|":
        return result.union(operand)
    elif operator == "~":
        return result.union(all_indexes.difference(operand))


def search(string, inverted_index, morph):
    operators = ("&", "|", "~")
    words = string.strip().split()
    all_indexes = set().union(*inverted_index.values())
    result = set()
    i = 0

    while i < len(words):
        word = words[i]

        if i + 1 != len(words) and word in operators:
            operator, next_word = word, words[i + 1]
            operand = inverted_index.get(get_normal_form(next_word, morph), set())
            result = apply_operator(operator, result, operand, all_indexes)
            i += 1
        elif word.startswith("~"):
            operand = inverted_index.get(get_normal_form(word[1:], morph), set())
            result = apply_operator("~", result, operand, all_indexes)
        else:
            operand = inverted_index.get(get_normal_form(word, morph), set())
            result = apply_operator("|", result, operand, all_indexes)

        i += 1

    return result


if __name__ == "__main__":
    morph = pymorphy2.MorphAnalyzer()

    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as file:
            inverted_index = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при чтении файла {INDEX_PATH}: {e}")
        inverted_index = defaultdict(set)

    user_input = input("Введите запрос в формате 'слово |& ~слово': ")
    results = search(user_input, inverted_index, morph)
    print(f"{user_input}: {'Нет совпадений' if not results else results}")
