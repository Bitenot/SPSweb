import re
import json
import fitz  # PyMuPDF
from ebooklib import epub
from bs4 import BeautifulSoup
import zipfile
import os

def load_words_from_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception as e:
        print(f"Ошибка при чтении файла со словами: {e}")
        return []

def get_user_settings():
    print("Режим поиска:\n1 - Точное совпадение\n2 - Расширенное совпадение (вхождение в слово)")
    mode = input("Выберите режим (1 или 2): ").strip()
    print("Режим вывода:\n1 - Сохранить в TXT\n2 - Сохранить в JSON\n3 - Вывод в консоль")
    output_mode = input("Выберите вариант (1, 2 или 3): ").strip()
    return mode == '2', output_mode

def search_words_in_text(text, words, fuzzy=False):
    results = {word: {'count': 0, 'pages': []} for word in words}
    for page_num, page in enumerate(text):
        page_lower = page.lower()
        for word in words:
            if fuzzy:
                matches = re.findall(r'\w*' + re.escape(word) + r'\w*', page_lower)
            else:
                matches = re.findall(r'\b' + re.escape(word) + r'\b', page_lower)
            if matches:
                results[word]['count'] += len(matches)
                results[word]['pages'].append(page_num + 1)
    return results

def extract_text_pdf(file_path):
    doc = fitz.open(file_path)
    return [page.get_text() for page in doc]

def extract_text_fb2(file_path):
    if file_path.lower().endswith('.zip') or file_path.lower().endswith('.fb2.zip'):
        with zipfile.ZipFile(file_path) as z:
            for name in z.namelist():
                if name.endswith('.fb2'):
                    with z.open(name) as f:
                        soup = BeautifulSoup(f.read(), 'lxml')
                        return [soup.get_text()]
        raise ValueError("Архив не содержит .fb2 файла.")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
            return [soup.get_text()]

def extract_text_epub(file_path):
    book = epub.read_epub(file_path)
    text = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text.append(soup.get_text())
    return text

def output_results(results, mode):
    if mode == '1':
        with open('results.txt', 'w', encoding='utf-8') as f:
            for word, data in results.items():
                f.write(f"{word} — совпадений: {data['count']}, страницы: {data['pages']}\n")
        print("Результаты сохранены в results.txt")
    elif mode == '2':
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Результаты сохранены в results.json")
    else:
        for word, data in results.items():
            print(f"{word} — совпадений: {data['count']}, страницы: {data['pages']}")

def main():
    file_path = input("Введите путь к файлу книги (PDF, FB2, EPUB): ").strip()
    word_file = "C:\\txt.txt"  # Путь к файлу со словами
    words = load_words_from_file(word_file)

    if not words:
        print("Список слов пуст. Проверьте файл txt.txt")
        return

    fuzzy, output_mode = get_user_settings()

    # Определяем формат книги
    try:
        if file_path.lower().endswith('.pdf'):
            text = extract_text_pdf(file_path)
        elif file_path.lower().endswith('.fb2') or file_path.lower().endswith('.fb2.zip') or file_path.lower().endswith('.zip'):
            text = extract_text_fb2(file_path)
        elif file_path.lower().endswith('.epub'):
            text = extract_text_epub(file_path)
        else:
            print("Неподдерживаемый формат файла.")
            return
    except Exception as e:
        print(f"Ошибка чтения книги: {e}")
        return

    results = search_words_in_text(text, words, fuzzy)
    output_results(results, output_mode)

if __name__ == "__main__":
    main()
