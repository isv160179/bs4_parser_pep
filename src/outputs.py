import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import DATETIME_FORMAT, BASE_DIR
from utils import create_dir


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    create_dir(results_dir)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


def control_output(results, cli_args):
    # output = {
    #     ArgumentOutput.RESULT_IN_TABLE: lambda: pretty_output(results),
    #     ArgumentOutput.RESULT_IN_FILE: lambda: file_output(results, cli_args),
    # }.get(cli_args.output, lambda: default_output(results))
    output = {
        'pretty': lambda: pretty_output(results),
        'file': lambda: file_output(results, cli_args),
    }.get(cli_args.output, lambda: default_output(results))
    output()


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)
