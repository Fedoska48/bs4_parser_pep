import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import DATETIME_FORMAT, BASE_DIR

# MESSAGES
RESULT_FILE_MESSAGE = 'Файл с результатами был сохранён: {}'


def control_output(results, cli_args):
    output_data = {
        'pretty': pretty_output,
        'file': file_output,
        None: default_output
    }
    output_data[cli_args.output](results, cli_args)


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    # Я понял про вынос в константы, но в данном случае это влияет на автотест
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parse_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    filename = f'{parse_mode}_{now_formatted}.csv'
    file_path = results_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)

    # logs
    logging.info(RESULT_FILE_MESSAGE.format(file_path))
