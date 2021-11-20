import os
import requests
import hashlib
from bs4 import BeautifulSoup

TARGET_URL = 'https://education.sdsc.edu/studenttech/rehs/'


def get_page(target_url: str):
    rq = requests.get(target_url)
    if not rq.status_code == 200:
        raise IOError(f'Status code for request was not 200; instead it was {rq.status_code}')
    return rq


def safe_filename(unsafe: str):
    keep_characters = (' ', '.', '_')
    return "".join(c for c in unsafe if c.isalnum() or c in keep_characters).rstrip()


def get_filename(target_url: str):
    if target_url.split('/')[-1] == '':
        return safe_filename(target_url.split('/')[-2])
    return safe_filename(target_url.split('/')[-1])


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


def post_message(name: str, content: str):
    with open('discord_hook.txt', 'r') as f:
        hook_url = f.read().strip()
    structure = {'content': content, 'username': name}
    r = requests.post(hook_url, json=structure)
    return r.status_code


def scrape(target_url: str):
    """
    Hit the website, scan contents, etc. (Main func)
    :return:
    """
    hit = get_page(target_url)
    output_filename = get_filename(target_url)
    old = get_old_hash(f'storage/{output_filename}.sum')
    soup = BeautifulSoup(hit.content, features="html.parser")
    found_element = soup.select_one('#page')  # There's a "recommendations" bar at the bottom that changes every time.
    current = hash_it(bytes(found_element.getText(), 'utf-8'))
    if old != current:
        print(f'Changed! {old[-10:]} -> {current[-10:]}')
        post_message(f'{output_filename} file change', f'Page updated:\n{target_url}')
    else:
        print(f'didn\'t change {old[-10:]} = {current[-10:]}')
    write_new_hash(f'storage/{output_filename}.sum', current)


if __name__ == '__main__':
    scrape(TARGET_URL)
