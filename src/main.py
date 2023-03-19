# main.py
import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # session = requests_cache.CachedSession()
    # response = session.get(whats_new_url)
    # response.encoding = 'utf-8'
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        session = requests_cache.CachedSession()
        # response = session.get(version_link)
        # response.encoding = 'utf-8'
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    # session = requests_cache.CachedSession()
    # response = session.get(MAIN_DOC_URL)
    # response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        link = a_tag['href']
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # session = requests_cache.CachedSession()
    # response = session.get(downloads_url)
    # response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table = soup.find(attrs={'class': 'docutils'})
    pattern = r'.+pdf-a4\.zip$'
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(pattern)})
    link = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = link.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(link)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    # logs
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    # session = requests_cache.CachedSession()
    # response = session.get(PEP_URL)
    # response.encoding = 'utf-8'
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    data_table = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
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
    for link in tqdm(full_links):
        session = requests_cache.CachedSession()
        response = session.get(link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        data_page = soup.find('dl',
                              attrs={'class': 'rfc2822 field-list simple'})
        status_page = data_page.find('abbr')
        link_page = link.split('/')[-1]
        status_full_page.append(
            (link_page, status_page.text)
        )
    list_of_keys = [i[1] for i in status_full_page]
    result_page = [(i[0], i[1][:1]) for i in status_full_page]
    count = {key: 0 for key in list_of_keys}
    total = 0
    for x in range(len(result_page)):
        if result_page[x] not in result_table:
            logging.info(f'Данные {result_page[x][0]} отличаются от табличных')
            continue
        count[status_full_page[x][1]] += 1
        total += 1
    count['Total'] = total
    results = [('Статус', 'Кол-во')]
    for result in count.items():
        results.append(result)
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    # logs
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    # logs
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clean_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)

    # logs
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()