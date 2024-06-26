import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_string(soap, string):
    searching_string = soap.find(string=string)
    if searching_string is None:
        error_msg = f'Не найдена строка {string}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searching_string


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, 'lxml')


def create_dir(dir_name):
    try:
        dir_name.mkdir(exist_ok=True)
    except PermissionError:
        logging.fatal(f'У вас нет прав для создания папки {dir_name}')
        exit(1)
    except FileNotFoundError:
        logging.fatal(f'Путь {dir_name} не найден.')
        exit(1)
    except OSError as error:
        logging.fatal(
            f'При создании директории {dir_name} возникла ошибка: {error}'
        )
        exit(1)
