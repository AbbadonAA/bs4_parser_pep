import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    """Выбор формата вывода."""
    outputs = {
        'pretty': pretty_output,
        'file': file_output,
        '': default_output
    }
    output = cli_args.output
    if not output:
        output = ''
    outputs[output](results, cli_args)


def file_output(results, cli_args):
    """Создание директории и запись результата в файл."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


def pretty_output(results, cli_args):
    """Вывод результата в табличной форме в терминал."""
    try:
        table = PrettyTable()
        table.field_names = results[0]
        table.align = 'l'
        table.add_rows(results[1:])
        print(table)
    except Exception as error:
        logging.error(f'Возникла ошибка вывода: {error}')


def default_output(results, cli_args):
    """Построчный вывод в терминал."""
    for row in results:
        print(*row)
