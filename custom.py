import re

from bs4 import BeautifulSoup


def rehs_application(bs: BeautifulSoup) -> str:  # all search methods must have this signature
    return re.sub(r'\n{3,}', '\n\n', bs.find('main', id="content", role="main").get_text())
