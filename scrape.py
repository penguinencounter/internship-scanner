import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib

TARGET_URL = 'https://sdsc.edu/education_and_training/internships.html'


def get_page(target_url: str):
    rq = requests.get(TARGET_URL)
    if not rq.status_code == 200:
        raise IOError(f'Status code for request was not 200; instead it was {rq.status_code}')
    return rq


def get_filename(target_url: str):
    return target_url.split('/')[-1]+'.sum'


def hash_it(content: bytes):
    return hashlib.sha256(content).hexdigest()


def get_old_hash(file_path: str):
    content = ''
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
    return content


def write_new_hash(file_path: str, content: str):
    with open(file_path, 'w') as f:
        f.write(content)


def scrape(target_url: str):
    """
    Hit the website, scan contents, etc. (Main func)
    :return:
    """
    hit = get_page(target_url)
    output_filename = get_filename(target_url)
    old = get_old_hash(f'storage/{output_filename}')
    current = hash_it(hit.content)
    if old != current:
        print(f'Changed! {old[-10:]} -> {current[-10:]}')
    else:
        print(f'didn\'t change {old[-10:]} = {current[-10:]}')
    write_new_hash(f'storage/{output_filename}', current)



if __name__ == '__main__':
    scrape(TARGET_URL)