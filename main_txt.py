"""скрипт: бесконечный цикл чтения строк из текстового файла
"""
import configparser  # модуль для работы с .ini
import json
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

import const  # мой файл с контанстами


def wait(time_interval: int):
    """Функция разделяет процесс ожидания на отдельные интервалы ms,
    позволяя реализовать прерывание процесса sleep непосредственно во время процесса sleep
    """
    delta_sleep: int = (
        50  # интервал 50 мс - это гарантированных два-три нажатия на клавишу
    )
    step_sleep = time_interval // delta_sleep

    i: int = 1  # лучше называть переменную полными словами, описывающими на
    # что она ссылается, напиример 'interval_counter'
    while i < step_sleep:
        i += 1
        time.sleep(0.05)


def get_file_name() -> tuple[str]:
    """Определяем абсолютные пути текстовых файлов проекта"""
    # {WindowsPath} C:\Users\user\PycharmProjects\Lesson_01
    project_directory = Path(__file__).resolve(strict=True).parent

    # str "C:\\Users\\user\\PycharmProjects\\Lesson_01\\Text\\settings.ini"
    name_set_ini = str(project_directory / const.SET_INI)

    # str "C:\\Users\\user\\PycharmProjects\\Lesson_01\\Text\\queries.txt"
    name_queries_txt = str(project_directory / const.QUERIES_TXT)

    return name_set_ini, name_queries_txt


def replace_symbol(string: str) -> str:
    # it's better to rename to 'replace_prohibited_symbols'
    """Функция возвращает строку без запрещённых / нежелательных символов в имени файла"""
    string = string.replace(" ", "")
    string = string.replace(".", "_")
    string = string.replace("\\", "/")
    return string


def read_ini(file_name: str) -> tuple:
    """чтение конфигурационного параметра из файла .ini"""
    conf = configparser.RawConfigParser()
    conf.read(file_name)

    result = (
        conf.getint("base_settings", "start_string"),  # 1. method name like we
        # are getting int here, but arguments say about string
        # 2. couldn't install dependencies
        # [pipenv.exceptions.ResolutionFailure]: Warning: Your dependencies
        # could not be resolved. You likely have a mismatch in your
        # sub-dependencies.
        conf.getint("base_settings", "wait_interval"),
        conf.getint("base_settings", "search_page_number"),
    )
    # print(result)  # it's better to study pdb, PyCharm debugger and use
    # them instead of print()
    return result


def write_ini(file_name: str, number: int, conf_par_value: Optional[int]):
    """запись конфигурационного параметра в файл .ini"""
    section = "base_settings"

    # 1: стартовая строка чтения из файла queries.txt
    if number == 1:
        parameter = "start_string"

    # 2: интервал опроса поисковых систем, мс
    elif number == 2:
        parameter = "wait_interval"

    # 3: количество загружаемых поисковых страниц
    elif number == 3:
        parameter = "search_page_number"

    # 4: заглушка
    else:
        print("ошибка записи: параметр не найден!")
        return

    conf = configparser.RawConfigParser()
    conf.read(file_name)
    conf.set(section, parameter, conf_par_value)

    with open(file_name, "w", encoding="utf-8") as config:
        conf.write(config)


def get_link(link: str) -> str:
    """вынимаем ссылку из исходной строки, примеры:
    <a href="/url?q=https://www.python.org/&amp;sa=U&amp;ved=2ahUKEwic0Oa5m ... /a>
    <a href="/url?q=https://ru.wikipedia.org/wiki/Python&amp;sa=U&amp;ved=2 ...
    т.е. в исходной строке ссылка начинается на "http" и заканчивается ДО амперсанда "&amp"
    """
    url_start_index = link.find("http")
    url_stop_index = link.find("&amp")

    if url_start_index == -1 or url_stop_index == -1:
        return ""

    link = link[url_start_index:url_stop_index]
    return link


def parsing(line: str, pages: int) -> list[dict[str, str]]:
    """получаем ссылки из страницы"""
    result_list: list = []  # основной список словарей для результатов

    for i in range(1, pages + 1):  # rename 'i' to speaking name
        url = "https://www.google.ru/search?q=" + line + "&start=" + str((i - 1) * 10)

        # проверка: вывод фактического url, отправленного поисковику
        # print(url)

        page = requests.get(url)
        # проверочная ссылка, чтобы получить page.status_code != 200
        # page = requests.get('https://www.yandex.ru/404')

        if page.status_code != 200:
            print(page.status_code)

        else:
            soup = BeautifulSoup(
                page.content, "html.parser"
            )  # html.parser встроен в Python
            # print(soup.prettify())

            # ищем на html-странице soup все тэги <h3> (заголовки наших поисковых ссылок)
            # и формируем список [link_name] для тэгов <h3>, содержащих название ссылки
            link_names_list = soup.findAll("h3")

            for link_name in link_names_list:
                # находим родительский тэг <a> для <h3>, вытаскиваем из него ссылку
                # и помещаем ссылку в список [link_object]
                link_object = get_link(str(link_name.find_parent("a")))

                # вывод на печать значений != None:
                if link_object is not None and link_name is not None:
                    # print(link_object + " " + link_name.text)
                    result_list.append({"link": link_object, "text": link_name.text})
    return result_list


def main():
    """скрипт: бесконечный цикл чтения строк из текстового файла"""
    # определяем абсолютные имена текстовых файлов из const.py:
    file_names: tuple[str] = get_file_name()  # есть указание типов для
    # переменных. В названии тип не указывается
    file_name_set_ini = file_names[0]
    file_name_queries_txt = file_names[1]

    # читаем настройки из ini-файла:
    start_settings = read_ini(file_name_set_ini)

    # извлекаем из кортежа tuple значения начальных настроек:
    # наличие большого количества комментариев говорит о том, что нужно
    # выбрать другую структуру данных, например именованный кортеж или
    # словарь и дать имена полей, например:
    # start_row_number, query_interval, page_quantity
    start = start_settings[0]  # номер "стартовой" строки
    wait_ms = start_settings[1]  # интервал опроса
    pages = start_settings[2]  # количество запрашиваемых страниц поиска

    # проверка:
    print("Стартовая строка:", start)

    # бесконечный цикл:
    while True:
        try:
            with open(file_name_queries_txt, "r", encoding="utf-8") as query_file:
                # лучше читать по одной строке или указывать ограничение по
                # байтам - сколько скачивать, чтобы контролировать
                # использование памяти
                contents = query_file.readlines()

                # не понятно почему начинаем со строки, идущей перед стартовой
                for current in range(start - 1, len(contents)):
                    line = contents[current].strip()

                    print("========================")
                    print(line)
                    print("========================")

                    # здесь запускаем функцию parsing
                    link_list: list[dict] = parsing(line, pages)

                    # вывод содержимого списка словарей (Link_list) на печать:
                    for current_link in link_list:
                        # + concatenation is the slowest type of string
                        # formatting. f-string the fastest
                        print(f"{current_link['link']} {current_link['text']}")

                    # ждём секунду:
                    wait(wait_ms)

                # следующий цикл считывания начинаемс первой строки:
                start = 1

        # обрабатываем исключение прерывания "Stop" или "Ctrl-C":
        except KeyboardInterrupt:
            # записываем в .ini "стартовую" строку для следующего запуска:
            # несмотря на наличие возможности сохранять программно в
            # конфигурационный файл, это плохая практика и может привести к
            # багам, которые сложно диагностировать. Нужно будет идти в
            # контейнер, где развёрнуто приложение и там смотреть состояние.
            # обычно, конфигурационные файлы статичны и меняются переменными
            # окружения. В данном случае лучше использовать отдельный файл
            # для этой цели.
            write_ini(file_name_set_ini, 1, current + 2)

            # завершаем процесс:
            sys.exit()


def add_new_queries(new_queries: str, file_name_queries_txt: str) -> bool:
    """Функция добавляет новый запрос new_queries в файл file_name_queries_txt
    ответ на POST-запрос
    Хорошо бы высокоуровнево описать здесь в каком случае
    возвращается True / False
    """
    try:
        with open(file_name_queries_txt, "a", encoding="utf-8") as file:
            try:
                file.writelines(new_queries.replace("_", " ") + "\n")
                # print("Новый запрос успешно записан в файл")
                return True
            except OSError:
                print("Ошибка добавления нового запроса в файл!")
                return False
    except OSError:  # OSError - файл не найден или диск полон
        print("Файл не найден!")
        return False


def get_all_queries(file_name_queries_txt: str) -> json:
    """Функция формирует перечень всех запросов
    ответ на GET-запрос
    """
    try:
        with open(file_name_queries_txt, "r", encoding="utf-8") as file:

            lines = file.readlines()  # построчно считали файл
            lines = [line.rstrip("\n") for line in lines]  # это лист []

            # формируем json "ключ: лист", для вывода русских букв добавляем ensure_ascii=False
            get_all_request_json = json.dumps({"queries": lines}, ensure_ascii=False)

            print(get_all_request_json)
            return get_all_request_json
    except OSError:  # OSError - файл не найден или диск полон:
        return "Файл не найден!"


def clear_text_file(file_name: str):
    # имя и докстринга функции не соответствуют телу
    """Функция очищает файл file_name
    ответ на DELETE-запрос
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.seek(0)


def save_file_html(searh_phrase: str):
    """временная функция"""
    # уже писал про конкатинацию. Кроме того, для УРЛ лучше использовать
    # специальные библиотеки для корректной сборку урла. Например,
    # >>> from yarl import URL
    # >>> url = URL('https://www.python.org/~guido?arg=1#frag')
    # >>> url
    # URL('https://www.python.org/~guido?arg=1#frag')
    # >>> url.human_repr()
    # 'https://www.python.org/путь'
    # For full documentation please read https://yarl.readthedocs.org.
    url = "https://www.google.ru/search?q=" + searh_phrase + '&start="10'
    response = requests.get(url)  # url - ссылка
    page_html = response.text
    print(page_html)
    return page_html


def new_parse(page):
    """временная функция"""
    soup = BeautifulSoup(page, "html.parser")

    link_names_list = soup.findAll("h3")

    for link_name in link_names_list:
        # находим родительский тэг <a> для <h3>, вытаскиваем из него ссылку
        # и помещаем ссылку в список [link_object]
        link_object = get_link(str(link_name.find_parent("a")))

        # вывод на печать значений != None:
        if any(link_object) and any(link_name):
            print(link_object + " " + link_name.text)


def temp_print_settings(file_name_set_ini: str) -> int:
    """извлекаем номер стартовой строки"""
    start_settings = read_ini(file_name_set_ini)
    # извлекаем из кортежа tuple значения начальных настроек:
    print(start_settings[0])  # номер "стартовой" строки
    return start_settings[0]


def print_string_from_file(file_path: str, string_number: int):
    """распечатываем стартовую строку по её номеру"""
    print(string_number)
    with open(file_path, "r", encoding="utf-8") as query_file:
        information = query_file.readlines()
    my_string = information[string_number - 1].strip()
    print(my_string)
    return my_string


if __name__ == "__main__":
    main()
