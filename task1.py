import os
import requests
import shutil

from bs4 import BeautifulSoup

site_url = "https://vc.ru"

data_dir = "data"
pages_number = 200
output = "download"


def crawl_pages(start_id: int, num_pages: int):

    pages_index = {}

    for page_id in range(start_id, start_id + num_pages):
        page_url = f"{site_url}/{page_id}"
        page_filename = os.path.join(data_dir, f"{page_id}.html")

        with requests.get(page_url) as response:
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for data in soup(['style', 'script', 'link']):
                    data.decompose()
                page_content = str(soup)

                with open(page_filename, "w", encoding="utf-8") as page_file:
                    page_file.write(page_content)
                pages_index[page_id] = page_url

            progress = (f"Page {page_id} | Index ({len(pages_index)}/{num_pages}) "
                        f"| Status Code: {response.status_code}")
            print(progress.ljust(62, " "))

    return pages_index


def create_result_files(pages_index):

    with open(os.path.join(data_dir, "index.txt"), "w", encoding="utf-8") as index_txt:
        content = [f"{key} {pages_index[key]}" for key in pages_index.keys()]
        index_txt.write("\n".join(content))

    shutil.make_archive(output, 'zip', data_dir)


def create_or_remove_dir():
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.mkdir(data_dir)


if __name__ == '__main__':
    create_or_remove_dir()
    index = crawl_pages(start_id=654321, num_pages=pages_number)
    create_result_files(index)
