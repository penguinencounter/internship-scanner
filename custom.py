import hashlib
import json
import re

import bs4
from bs4 import BeautifulSoup


def rehs_application(bs: BeautifulSoup) -> str:  # all search methods must have this signature
    return re.sub(r'\n{3,}', '\n\n', bs.find('main', id="content", role="main").get_text())


# Does not support parse=true!
def gh_release_tracker(content: str) -> str:
    if not isinstance(content, str):
        raise TypeError('gh_release_tracker only supports parse=false, sorry!')
    d = json.loads(content)
    new = ''
    for release in d:
        new += f'{release["name"]} | {release["tag_name"]} @ {release["target_commitish"]}\n'
    return new


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def royalroad_chapters(bs: BeautifulSoup) -> str:
    container = bs.find('table', id='chapters')
    chapter_count = container.get("data-chapters", "unknown")
    chapters = container.findAll('tr', class_='chapter-row')
    result = ''
    for chapter in chapters:
        title: bs4.Tag = next(filter(lambda el: el.get("class", "__ok__") != "text-right", chapter.findAll('td')))
        anchor = title.find('a')
        result += f'* {anchor.get_text().strip()}\n'
        result += '    ' + anchor.get('href') + '\n'
    result += '\n[ ' + chapter_count + ' chapters ]'
    return result


def royalroad_fictions(bs: BeautifulSoup) -> str:
    all_fictions = bs.findAll(class_='cover')
    result = ''
    for fiction in all_fictions:
        title_name = (
            fiction.parent
            .find('div', class_='mt-overlay')
            .find('h2', recursive=False)
            .find(text=True, recursive=False)
        )
        result += f'* {title_name.strip()}\n'
    return result
