import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from setuptools._vendor.more_itertools import take
from tqdm import tqdm

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

PEP_URL = 'https://peps.python.org/'

if __name__ == '__main__':
    session = requests_cache.CachedSession()
    response = session.get(PEP_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    data_table = soup.find('section', attrs={'id': 'index-by-category'})
    refs = data_table.find_all('a', attrs={'class': 'pep reference internal'})
    abbrs = data_table.find_all('abbr')
    statuses = []
    for abbr in tqdm(abbrs):
        preview_status = abbr.text[1:]
        if preview_status is not None:
            preview_status = preview_status
        else:
            preview_status = ''
        statuses.append(preview_status)
    ids = []
    titles = []
    full_links = []
    for ref in tqdm(refs):
        id = ref['href']
        if len(ref.text) > 4:
            ids.append(id)
        if id not in ids:
            full_link = urljoin(PEP_URL, id)
            full_links.append(full_link)
    result_table = list(zip(ids, statuses))
    status_full_page = []
    for link in tqdm(full_links[:5]):
        session = requests_cache.CachedSession()
        response = session.get(link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        data_page = soup.find('dl',
                              attrs={'class': 'rfc2822 field-list simple'})
        status_page = data_page.find('abbr')
        title_page = soup.find('h1', attrs={'class': 'page-title'})
        link_page = link.split('/')[-1]
        status_full_page.append(
            (link_page, status_page.text)
        )
    list_of_keys = [i[1] for i in status_full_page]
    result_page = [(i[0], i[1][:1]) for i in status_full_page]
    count = {}
    count = {key: 0 for key in list_of_keys}
    total = 0
    for x in range(len(result_page)):
        if result_page[x] not in result_table:
            logging.info(f'Данные {result_page[x][0]} отличаются от табличных')
            continue
        count[status_full_page[x][1]] += 1
        total += 1
    count['Total'] = total
    for result in count.items():
        print(*result)
