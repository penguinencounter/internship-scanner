import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

TARGET_URL = 'https://sdsc.edu/education_and_training/internships.html'
DATE_FORMAT = '%m%d%Y_%I%M%S%p'  # MMDDYYYY_HRMISEAM


def get_page():
    rqo = requests.get(TARGET_URL)


def scrape():
    """
    Hit the website, scan contents, etc. (Main func)
    :return:
    """
    hit = requests.get(TARGET_URL)
    if not hit.status_code == 200:
        raise IOError(f'Status code for request was not 200; instead it was {hit.status_code}')
    date = datetime.now().strftime(DATE_FORMAT)  # Encode string according to current time and DATE_FORMAT
    print(f'[{date}] Download success!')
    real_filename = TARGET_URL.split('/')[-1]  # Name of the downloaded file, according to the URL
    output_filename = f'{date}_{real_filename}'
    with open(f'history/{output_filename}', 'wb') as f:
        f.write(hit.content)
    soup = BeautifulSoup(hit.text, 'html.parser')


if __name__ == '__main__':
    compare('Hello World', 'Hello there, World')
