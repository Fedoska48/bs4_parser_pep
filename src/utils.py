# utils.py
import logging

import requests_cache
from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

# MESSAGES
DIFFERENCE_DATA = 'Статус {} отличается. Таблица: {} Страница: {}.'
REQUEST_EXCEPTION = 'Возникла ошибка при загрузке страницы {}'
TAG_NOT_FOUND = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    """Перехват ошибки RequestException."""
    try:
        response = session.get(url)
        response.encoding = encoding
        if response is None:
            return
        return response
    except RequestException:
        raise RequestException(
            REQUEST_EXCEPTION.format(url),
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки ParserFindTagException."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND.format(tag, attrs))
    return searched_tag


def get_soup(response, features='lxml'):
    """Получение "супа"."""
    return BeautifulSoup(response.text, features)


def get_sections_by_selector(soup, selector):
    """Получение данных по селектору"""
    return soup.select(selector)


# Получение данных: полная ссылка на страницу pep и статус
def get_data_peps_page(links_list, session=requests_cache.CachedSession()):
    try:
        status_full_page = {}
        for link in links_list:
            soup = get_soup(get_response(session, link))
            status_page = soup.select_one('#pep-content abbr')
            link_page = link.split('/')[-1]
            status_full_page[link_page] = status_page.text
        return status_full_page
    except RequestException:
        raise RequestException(
            REQUEST_EXCEPTION.format(link),
            stack_info=True
        )


def count_statuses(pep_data_table, data_pages):
    count = {key: 0 for key in data_pages.values()}
    for item in data_pages.items():
        key = item[0]
        if data_pages[key] != pep_data_table[key]:
            logging.info(
                DIFFERENCE_DATA.format(key, pep_data_table[key],
                                       data_pages[key]))
        count[data_pages[key]] += 1
    return count
