# Python DOCS Parser

## Описание

Учебный проект для практики создания парсеров.

Парсится документация Python: PEP, версии, обновления, архив с документацией.

В проекте реализован парсинг аргументов командной строки для выбора режима работы программы. Всего доступно четыре режима:
- **whats-new** (получение списка ссылок на перечень изменений в версиях Python)
- **latest-versions** (получение списка ссылок на документацию для всех версий Python)
- **download** (скачивание архива с документацией для последней версии Python)
- **pep** (получение данных о статусах всех PEP и вывод информации о несоответствиях статусов в общем списке и в карточках отдельных PEP)

Реализована возможность выбора формата вывода:
- стандартный вывод в терминал;
- вывод в терминал в табличной форме (prettytable);
- запись результатов работы в файл .csv.

Настроено логирование - логи выводятся в терминал и сохраняются в отдельной директории с ротацией.

## Ключевые технологии и библиотеки:
- [Python](https://www.python.org/);
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/);
- [requests_cache](https://pypi.org/project/requests-cache/);
- [argparse](https://docs.python.org/3/library/argparse.html);
- [prettytable](https://pypi.org/project/prettytable/);
- [tqdm](https://pypi.org/project/tqdm/).

## Установка
1. Склонируйте репозиторий:
```
git clone git@github.com:AbbadonAA/bs4_parser_pep.git
```
2. Активируйте venv и установите зависимости:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Проект готов к запуску из директории src:
```
python src/main.py
```
## Управление:

Вызов справки по доступным аргументам:
```
python src/main.py -h
```

Выбор режима работы:
```
python src/main.py whats-new
```
```
python src/main.py latest-versions
```
```
python src/main.py download
```
```
python src/main.py pep
```
Доступные опциональные аргументы:
- **-o {pretty, file}, --output {pretty, file}**; - дополнительные способы вывода данных (pretty - табличный формат вывода в терминал, file - запись данных в файл .csv). Стандартный вывод - построчно в терминал.
- **-с, --clear-cache**; - очистка кеша. При первом запуске загруженная страница кешируется. Без данного параметра последующие запуски будут обрабатывать данные в кеше.

## Лицензия
- ### **MIT License**

### Автор
Pushkarev Anton

pushkarevantona@gmail.com


