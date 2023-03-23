# Проект парсинга pep

### Технологический стек

Python 3.9, BeautifulSoup4

### Автор

Никита Сергеевич Федяев

Telegram: [@nsfed](https://t.me/nsfed)

### Режимы работы парсера:

- whats-new
- latest-versions
- download
- pep

### Файлы и директории

В папке **/downloads** находится результат режима работы download
В папке **/logs** находятся логи выполнения
В папке **/results** находится результат вывода данных в файл

### Подготовка к работе парсера

Клонирование репозитория:

*git clone git@github.com:Fedoska48/bs4_parser_pep.git*

Необходимо создать вирутальное окружение (способ зависит от операционной системы)

Здесь и ниже для Windows:

*python -m venv venv*

Активировать виртуальное окружение:

*source venv/Scripts/activate*

Установить зависимости:

*pip install -r requirements.txt*

## Инструкция:

Находясь в папке \src необходимо вызвать помощник по командам:

*python main.py -h*

**- whats-new**

### Команда для вывода последних обновлений Python:

*python main.py whats-new*

**- latest-versions**

### Команда для проверки последних версий Python:

*python main.py latest-versions*

**- download**

### Команда для скачивания документации в формате pdf в архиве:

*python main.py download*

**- pep**

### Команда для анализа статусов документации PEP:

*python main.py pep*

## Варианты вывода (на примере latest-versions)

### По умолчанию результат выводится в консоли

### Вывод в консоли с табличным форматирование pretty_table:

*python main.py latest-versions -o pretty*

### Экспорт в .csv файл:

*python main.py latest-versions -o file*
