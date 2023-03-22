# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_URL, LOG_DIR, MAIN_DOC_URL, PEP_URL,
                       WHATS_NEW_URL)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import (count_statuses, find_tag, get_data_peps_page, get_response,
                   get_sections_by_selector, get_soup)

# MESSAGES
DOWNLOAD_FINISHED_MESSAGE = 'Архив был загружен и сохранён: {}'
EMPTY_RESULT_MESSAGE = 'Ничего не нашлось'
EMPTY_RESPONSE_MESSAGE = 'Не был получен ответ по ссылке: {}'
FINAL_MESSAGE = 'Сбой в работе программы: {}'
# parser main function messages:
START_PARSER = 'Парсер запущен!'
ARG_PARSER = 'Аргументы командной строки: {}'
FINISHED_PARSER = 'Парсер завершил работу.'


def whats_new(session):
    """Получение нововведений версий Питона."""
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    soup = get_soup(get_response(session, WHATS_NEW_URL))
    selector = '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    sections = get_sections_by_selector(soup, selector)
    for section in tqdm(sections):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(WHATS_NEW_URL, href)
        session = requests_cache.CachedSession()
        response = get_response(session, version_link)
        if response is None:
            logging.warning(EMPTY_RESPONSE_MESSAGE.format(version_link))
            continue
        soup = get_soup(response)
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    return results


def latest_versions(session):
    """Поиск документаций послежних версий Питона."""
    soup = get_soup(get_response(session, MAIN_DOC_URL))
    selector = 'div.sphinxsidebarwrapper ul'
    ul_tags = get_sections_by_selector(soup, selector)
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise ParserFindTagException(EMPTY_RESULT_MESSAGE)
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
    soup = get_soup(get_response(session, DOWNLOAD_URL))
    pdf_a4 = soup.select_one('table.docutils a[href$="pdf-a4.zip"]')['href']
    pdf_a4_link = urljoin(DOWNLOAD_URL, pdf_a4)
    filename = pdf_a4_link.split('/')[-1]
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(pdf_a4_link)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    # logs
    logging.info(DOWNLOAD_FINISHED_MESSAGE.format(archive_path))


def pep(session):
    """Подсчет количество статусов PEP"""
    soup = get_soup(get_response(session, PEP_URL))
    data_table = soup.select('#numerical-index tbody > tr')
    pep_data_table = {}  # pep_id: status_table
    for data in data_table:
        pep_id_table = find_tag(data, 'a')['href']
        status_table = find_tag(data, 'abbr')['title'].split()[1]
        pep_data_table[pep_id_table] = status_table
    full_links_list = [urljoin(PEP_URL, i) for i in pep_data_table.keys()]
    data_pages = get_data_peps_page(full_links_list)
    return [
        ('Статус', 'Количество'),
        *count_statuses(pep_data_table, data_pages).items(),
        ('Всего', sum(count_statuses(pep_data_table, data_pages).values())),
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
        configure_logging(LOG_DIR)
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
