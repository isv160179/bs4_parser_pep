import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    MAIN_DOC_URL,
    MAIN_PEP_URL,
    EXPECTED_STATUS,
    PDF_FILES_IN_ZIP,
    PATTERN
)
from outputs import control_output
from utils import find_tag, get_soup, find_string, create_dir


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    main_div = find_tag(
        soup,
        'section',
        {'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div,
        'div',
        {'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all('li', {'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python, 'Ход выполнения:'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(session, version_link)
        if soup is None:
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl').text.replace('\n', ' ')
        results.append((version_link, h1.text, dl))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(
        soup,
        'div',
        {'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = PATTERN.search(a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': PDF_FILES_IN_ZIP}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    create_dir(downloads_dir)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, MAIN_PEP_URL)
    pep_list = find_tag(
        soup,
        'section',
        {'id': 'numerical-index'}
    )
    tbody_tag = find_tag(pep_list, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    status_count = {}
    for tr_tag in tqdm(tr_tags):
        preview_status = find_tag(tr_tag, 'abbr').text[1:]
        pep_url = urljoin(MAIN_PEP_URL, find_tag(tr_tag, 'a')['href'])
        soup = get_soup(session, pep_url)
        pep_status = find_string(
            soup, 'Status'
        ).parent.find_next_sibling('dd').string.strip()
        status_count[pep_status] = status_count.setdefault(pep_status, 0) + 1
        if pep_status not in EXPECTED_STATUS[preview_status]:
            error_message = (
                f'Несовпадающие статусы:\n'
                f'{pep_url}\n'
                f'Статус в карточке: {pep_status}\n'
                f'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
            )
            logging.warning(error_message)

    results = [('Статус', 'Количество')]
    results.extend(list(status_count.items()))
    results.append(('Total', len(tr_tags)))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
