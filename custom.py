import json
import re

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
