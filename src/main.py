# main.py
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DOWNLOAD_URL, MAIN_DOC_URL, PEP_URL, WHATS_NEW_URL
)
from exceptions import LatestVersionException
from outputs import control_output
from utils import find_tag, get_soup

# MESSAGES
DOWNLOAD_FINISHED_MESSAGE = 'Архив был загружен и сохранён: {}'
EMPTY_RESULT_MESSAGE = 'Ничего не нашлось'
EMPTY_RESPONSE_MESSAGE = 'Не был получен ответ по ссылке: {}'
FINAL_MESSAGE = 'Сбой в работе программы: {}'
DIFFERENCE_DATA = 'Статус {} отличается. Таблица: {} Страница: {}.'
# parser main function messages:
START_PARSER = 'Парсер запущен!'
ARG_PARSER = 'Аргументы командной строки: {}'
FINISHED_PARSER = 'Парсер завершил работу.'


def whats_new(session):
    """Получение нововведений версий Питона."""
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    logs = []
    for anchor in tqdm(
            get_soup(
                session, WHATS_NEW_URL
            ).select(
                '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
            )
    ):
        try:
            href = anchor['href']
            version_link = urljoin(WHATS_NEW_URL, href)
            soup = get_soup(session, version_link)
            results.append(
                (
                    version_link,
                    find_tag(soup, 'h1').text,
                    find_tag(soup, 'dl').text.replace('\n', ' ')
                )
            )
        except ConnectionError:
            raise ConnectionError(logs.append(
                EMPTY_RESPONSE_MESSAGE.format(version_link)
            ))
    list(map(logging.warning, logs))
    return results


def latest_versions(session):
    """Поиск документаций послежних версий Питона."""
    for ul in get_soup(
            session, MAIN_DOC_URL
    ).select(
        'div.sphinxsidebarwrapper ul'
    ):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise LatestVersionException(EMPTY_RESULT_MESSAGE)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in tqdm(a_tags):
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    """Скачивание архива с документацией"""
    downloads_dir = BASE_DIR / 'downloads'
    pdf_a4_link = urljoin(
        DOWNLOAD_URL, get_soup(
            session, DOWNLOAD_URL
        ).select_one(
            'table.docutils a[href$="pdf-a4.zip"]'
        )['href']
    )
    filename = pdf_a4_link.split('/')[-1]
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(pdf_a4_link)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_FINISHED_MESSAGE.format(archive_path))


def pep(session):
    """Подсчет количество статусов PEP"""
    logs = []
    pep_data_table = {}
    for data in get_soup(
            session, PEP_URL
    ).select(
        '#numerical-index tbody > tr'
    ):
        pep_id_table = find_tag(data, 'a')['href']
        status_table = find_tag(data, 'abbr')['title'].split()[1]
        pep_data_table[pep_id_table] = status_table
    links_list = [urljoin(PEP_URL, i) for i in pep_data_table.keys()]
    pep_data_pages = {}
    count_statuses = defaultdict(int)
    for link in links_list:
        try:
            status_page = get_soup(session, link).select_one(
                '#pep-content abbr'
            )
        except ConnectionError:
            raise ConnectionError(
                logs.append(EMPTY_RESPONSE_MESSAGE.format(link))
            )
            continue
        pep_id_page = link.split('/')[-1]
        pep_data_pages[pep_id_page] = status_page.text
        count_statuses[pep_data_pages[pep_id_page]] += 1
        if pep_data_pages[pep_id_page] != pep_data_table[pep_id_page]:
            logs.append(
                logging.warning(DIFFERENCE_DATA.format(
                    pep_id_page,
                    pep_data_table[pep_id_page],
                    pep_data_pages[pep_id_page])
                )
            )
    list(map(logging.warning, logs))
    return [
        ('Статус', 'Количество'),
        *count_statuses.items(),
        ('Всего', sum(count_statuses.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    try:
        # logs
        configure_logging()
        logging.info(START_PARSER)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        # logs
        logging.info(ARG_PARSER.format(args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
        # logs
        logging.info(FINISHED_PARSER)
    except Exception as error:
        logging.exception(FINAL_MESSAGE.format(error))


if __name__ == '__main__':
    main()
