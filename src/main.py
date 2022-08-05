import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_LIST_URL
from outputs import control_output
from utils import find_tag, get_response
from collections import Counter

PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
FILE = r'.+pdf-a4\.zip$'


def whats_new(session):
    """Получение перечня версий Python со ссылками на список изменений."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_ul.find_all('li', attrs={'class': 'toctree-l1'})
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        a_tag = section.find('a')
        href = a_tag['href']
        link = urljoin(whats_new_url, href)
        response = get_response(session, link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((link, h1.text, dl_text))
    return result


def latest_versions(session):
    """Получение ссылок на документацию Python для всех версий."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    """Загрузка архива с документацией на последнюю версию Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    link_table = find_tag(soup, 'table')
    pdf_a4_tag = find_tag(link_table, 'a', attrs={'href': re.compile(FILE)})
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Подсчет PEP по статусам."""
    response = get_response(session, PEP_LIST_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    num_index = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    pep_list = find_tag(num_index, 'tbody')
    pep_lines = pep_list.find_all('tr')
    total_pep_count = 0
    status_counter = Counter()
    results = [('Статус', 'Количество')]
    for pep_line in tqdm(pep_lines):
        total_pep_count += 1
        short_status = pep_line.find('td').text[1:]
        try:
            status_ext = EXPECTED_STATUS[short_status]
        except KeyError:
            status_ext = []
            logging.info(
                f'\nОшибочный статус в общем списке: {short_status}\n'
                f'Строка PEP: {pep_line}'
            )
        link = find_tag(pep_line, 'a')['href']
        full_link = urljoin(PEP_LIST_URL, link)
        response = get_response(session, full_link)
        if response is None:
            return
        soup = BeautifulSoup(response.text, 'lxml')
        dl_tag = find_tag(soup, 'dl')
        status_line = dl_tag.find(string='Status')
        if not status_line:
            logging.error(f'{full_link} - не найдена строка статуса')
            continue
        else:
            status_line = status_line.find_parent()
            status_int = status_line.next_sibling.next_sibling.string
            if status_int not in status_ext:
                logging.info(
                    '\nНесовпадение статусов:\n'
                    f'{full_link}\n'
                    f'Статус в карточке - {status_int}\n'
                    f'Ожидаемые статусы - {status_ext}'
                )
            status_counter[status_int] += 1
    for status, count in status_counter.items():
        results.append((status, count))
    sum_from_cards = sum(status_counter.values())
    if total_pep_count != sum_from_cards:
        logging.error(
            f'\n Ошибка в сумме:\n'
            f'Всего PEP: {total_pep_count}'
            f'Всего статусов из карточек: {sum_from_cards}'
        )
        results.append(('Total', sum_from_cards))
    else:
        results.append(('Total', total_pep_count))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен.')
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


if __name__ == "__main__":
    main()
