import difflib
import json
import os
from typing import *
from hashlib import sha256
import logging
# noinspection PyUnresolvedReferences
from importlib import import_module

import requests
from bs4 import BeautifulSoup
from requests import Session

import adapt


def safe_filename(name):
    keep_characters = (' ', '.', '_')
    return "".join(c for c in name if c.isalnum() or c in keep_characters).rstrip()


with open('discord.json') as f:
    DISCORD: dict = json.load(f)


class Watch:
    def __init__(
        self,
        url: str,
        select: Optional[Tuple[str, str]] = None,
        parse: bool = True,
        send_to: List[str] = None
    ):
        self.url = url
        self.select = select if select is not None else ('bs4', 'BeautifulSoup.get_text')  # module, function
        self.parse = parse
        self.send_to = send_to if send_to is not None else []
        self.my_session = Session()
        self.my_session.mount("https://", adapt.LenientHTTPAdapter())
        self.my_session.headers.update({
            "User-Agent": "notify-update/0.1.0 (contact penguinencounter2@gmail.com) python-requests/2.29.0",
            "X-Notify-Update": "0.1.0",
            "X-Task-Name": ':'.join(self.select)
        })

    def dump(self):
        return {'url': self.url, 'select': self.select, 'parse': self.parse, 'send_to': self.send_to}

    def __hash__(self):
        return hash((self.url, self.select, self.parse, tuple(self.send_to)))

    @classmethod
    def load(cls, data: dict):
        return cls(
            data['url'],
            data['select'] if 'select' in data else None,
            data['parse'] if 'parse' in data else True,
            data['send_to'] if 'send_to' in data else None
        )

    def get_selector(self):
        # PAIN
        return eval(f'import_module(\'{self.select[0]}\').{self.select[1]}')

    def run(self) -> str:
        response = self.my_session.get(self.url)
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


def post_message(name: str, target: str, content: str):
    structure = {'content': content, 'username': name}
    r = requests.post(target, json=structure)
    return r.status_code


def post_messages(name: str, targets: Iterable[str], content: str):
    for target in targets:
        post_message(name, target, content)


def upload_as_file(name: str, target: str, fname: str, content: bytes):
    files = {'files': (fname, content, 'text/plain')}
    additional = {'username': name, 'content': 'Diff of changes:'}
    r = requests.post(target, files=files, data=additional)
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
            old_content = b''

        new, content = watch.run_and_hash()

        # Check for possible user errors
        if len(watch.send_to) == 0:
            print(f'WARNING: {watch.url} has no send_to targets, no messages will be sent!')

        bad = False
        for target in watch.send_to:
            if target not in DISCORD:
                print(f'ERROR: {watch.url} has an invalid send_to target (\"{target}\") and is invalid!')
                bad = True
        if bad:
            print(f'NOTICE: {watch.url} skipped (invalid)')
            continue

        if old != new:
            print(f'Page {watch.url} changed: diff ', end="", flush=True)
            lines = content.splitlines(keepends=True)
            old_lines = old_content.splitlines(keepends=True)
            diff = ''.join(
                difflib.unified_diff(list(map(lambda x: x.decode('utf-8'), old_lines)),
                                     list(map(lambda x: x.decode('utf-8'), lines)), 'old', 'new', n=3)
            )

            print(f'post ', end="", flush=True)
            post_messages("Watch v2", map(DISCORD.get, watch.send_to), f"Change detected on <{watch.url}>")

            # upload diff (diff.diff)
            print(f'upload ', end="", flush=True)
            for target in watch.send_to:
                upload_as_file("Watch v2", DISCORD[target], f"{watch.get_page_name()}.diff", diff.encode())

            print(f'save ', end="", flush=True)
            with open(watch.get_file_sum_name(), 'w') as f:
                f.write(new)
            with open(watch.get_file_content_name(), 'wb') as f:
                f.write(content)
            print('done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loaded = []
    if os.path.exists('watches.json'):
        loaded = import_watches()

    if not os.path.exists('storage'):
        os.mkdir('storage')

    invoke(loaded)
    export_watches(loaded)
