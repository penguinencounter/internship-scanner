import difflib
import json
import os
from typing import *
from hashlib import sha256
from importlib import import_module

import requests
from bs4 import BeautifulSoup
from requests import get


def safe_filename(name):
    keep_characters = (' ', '.', '_')
    return "".join(c for c in name if c.isalnum() or c in keep_characters).rstrip()


class Watch:
    def __init__(self, url: str, select: Optional[Tuple[str, str]] = None, parse: bool = True):
        self.url = url
        self.select = select if select is not None else ('bs4', 'BeautifulSoup.get_text')  # module, function
        self.parse = parse

    def dump(self):
        return {'url': self.url, 'select': self.select, 'parse': self.parse}

    def __hash__(self):
        return hash((self.url, self.select, self.parse))

    @classmethod
    def load(cls, data: dict):
        return cls(data['url'], data['select'] if 'select' in data else None, data['parse'] if 'parse' in data else True)

    def get_selector(self):
        # PAIN
        return eval(f'import_module(\'{self.select[0]}\').{self.select[1]}')

    def run(self) -> str:
        response = get(self.url)
        if not response.ok:
            raise IOError(f'Could not get page; status code {response.status_code}')
        selector = self.get_selector()
        if self.parse:
            soup = BeautifulSoup(response.text, 'html.parser')
        else:
            soup = response.text
        return selector(soup)

    def run_and_hash(self) -> (str, bytes):
        resp = self.run().encode()
        return sha256(resp).hexdigest(), resp

    def get_page_name(self) -> str:
        if self.url.split('/')[-1] == '':
            return safe_filename(self.url.split('/')[-2])
        return safe_filename(self.url.split('/')[-1])

    def get_file_sum_name(self) -> str:
        h = sha256(self.url.encode()).hexdigest()[:16]
        return f'storage/{self.get_page_name()}_{h}.sum'

    def get_file_content_name(self) -> str:
        h = sha256(self.url.encode()).hexdigest()[:16]
        return f'storage/{self.get_page_name()}_{h}.content'


def export_watches(watches: List[Watch]):
    with open('watches.json', 'w') as f:
        f.write(json.dumps(list(map(Watch.dump, watches)), indent=4))


def import_watches():
    with open('watches.json', 'r') as f:
        return list(map(Watch.load, json.loads(f.read())))


def post_message(name: str, content: str):
    with open('discord_hook.txt', 'r') as f:
        hook_url = f.read().strip()
    structure = {'content': content, 'username': name}
    r = requests.post(hook_url, json=structure)
    return r.status_code


def upload_as_file(name: str, fname: str, content: bytes):
    with open('discord_hook.txt', 'r') as f:
        hook_url = f.read().strip()
    files = {'files': (fname, content, 'text/plain')}
    additional = {'username': name, 'content': 'Diff of changes:'}
    r = requests.post(hook_url, files=files, data=additional)
    return r.status_code


def invoke(watches: List[Watch]):
    for watch in watches:
        if os.path.exists(watch.get_file_sum_name()):
            with open(watch.get_file_sum_name(), 'r') as f:
                old = f.read()
        else:
            old = ''
        if os.path.exists(watch.get_file_content_name()):
            with open(watch.get_file_content_name(), 'rb') as f:
                old_content = f.read()
        else:
            old_content = b'N/A'

        new, content = watch.run_and_hash()
        if old != new:
            print(f'Page {watch.url} changed: diff ', end="", flush=True)
            lines = content.splitlines(keepends=True)
            old_lines = old_content.splitlines(keepends=True)
            diff = ''.join(
                difflib.unified_diff(list(map(lambda x: x.decode('utf-8'), old_lines)),
                                     list(map(lambda x: x.decode('utf-8'), lines)), 'old', 'new', n=3)
            )

            print(f'post ', end="", flush=True)
            post_message("Watch v2", f"Change detected on {watch.url}")

            # upload diff (diff.diff)
            print(f'upload ', end="", flush=True)
            upload_as_file("Watch v2", f"{watch.get_page_name()}.diff", diff.encode())

            print(f'save ', end="", flush=True)
            with open(watch.get_file_sum_name(), 'w') as f:
                f.write(new)
            with open(watch.get_file_content_name(), 'wb') as f:
                f.write(content)
            print('done')


if __name__ == '__main__':
    loaded = []
    if os.path.exists('watches.json'):
        loaded = import_watches()

    if not os.path.exists('storage'):
        os.mkdir('storage')

    invoke(loaded)
    export_watches(loaded)