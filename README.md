# Проект парсинга pep

### Подготовка к работе парсера

Необходимо создать вирутальное окружение (способ зависит от операционной системы)

Здесь и ниже для Windows:

*python -m venv venv*

Активировать виртуальное окружение:

*source venv/Scripts/activate*

Установить зависимости:

*pip install -r requirements.txt*

### Возможности парсера:

Находясь в папке \src необхождимо вызвать помощник по командам:

*python main.py -h*

- whats-new

Команда для вывода последних обновлений Python:

*python main.py whats-new*

- latest-versions

Команда для проверки последних версий Python:

*python main.py latest-versions*

- download

Команда для скачивания документации в формате pdf в архиве:

*python main.py download*

- pep

Команда для анализа состояний доекументации PEP:

*python main.py pep*

### Варианты вывода (на примере latest-versions)

По умолчанию результат выводится в консоли

Вывод в консоли с табличным форматирование pretty_table:

*python main.py latest-versions -o pretty*

Экспорт в .csv файл:

*python main.py latest-versions -o file*

