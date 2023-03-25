# utils.py
from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

# MESSAGES
REQUEST_EXCEPTION = 'Возникла ошибка при загрузке страницы {}'
TAG_NOT_FOUND = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    """Перехват ошибки RequestException."""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise ConnectionError(REQUEST_EXCEPTION.format(url))


def find_tag(soup, tag, attrs=None):
    """Перехват ошибки ParserFindTagException."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND.format(tag, attrs))
    return searched_tag


def get_soup(session, url, features='lxml'):
    """Получение "супа"."""
    return BeautifulSoup(get_response(session, url).text, features)
