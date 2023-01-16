# import - инстукция, подключающая модуль из стандартной библиотеки
import time
import json
from pathlib import Path
import requests
from lxml import html
from bs4 import BeautifulSoup
import configparser  # модуль для работы с .ini


def wait(ms):
    # интервал 50 мс - это гарантированных два-три нажатия на клавишу:
    n = ms // 50
    for i in range(n):
        time.sleep(0.05)


def read_ini(file_name, number):  # читаем конфигурационный файл .ini
    conf = configparser.RawConfigParser()

    conf.read(file_name)

    # 1: стартовая строка чтения из файла queries.txt
    if number == 1:
        if conf.has_option("base_settings", "start_string"):
            base_settings = conf.getint("base_settings", "start_string")

    # 2: интервал опроса поисковых систем, мс
    elif number == 2:
        if conf.has_option("base_settings", "wait_interval"):
            base_settings = conf.getint("base_settings", "wait_interval")

    # 3: количество загружаемых поисковых страниц
    elif number == 3:
        if conf.has_option("base_settings", "search_page_number"):
            base_settings = conf.getint("base_settings", "search_page_number")

    # 4: заглушка
    else:
        print("ошибка чтения: параметр не найден! значение по умолчанию = 1")
        base_settings = 1

    return base_settings


def write_ini(file_name, number, value):   # записываем параметр в конфигурационный файл .ini
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

    value = str(value)
    conf = configparser.RawConfigParser()
    conf.read(file_name)
    conf.set(section, parameter, value)

    with open(file_name, "w") as config:
        conf.write(config)


def get_link(temp_string):  # вытаскиваем из строки ссылку
    # примеры ссылок:
    # <a href="/url?q=https://www.python.org/&amp;sa=U&amp;ved=2ahUKEwic0Oa5m ...
    # <a href="/url?q=https://ru.wikipedia.org/wiki/Python&amp;sa=U&amp;ved=2 ...
    # т.е. в исходной строке ссылка начинается на "http" и заканчивается ДО амперсанда "&amp"

    a = temp_string.find("http")
    b = temp_string.find("&amp")

    if a == -1 or b == -1:
        return ""

    temp_string = temp_string[a:b]
    return temp_string


def parsing(line, pages):
    link_name   = []  # список для тэгов <h3>, содержащих название ссылки
    link_object = []  # список для тэгов <а>, содержащих собственно ссылку

    for i in range(1, pages + 1):
        url = "https://www.google.ru/search?q=" + line + "&start=" + str((i-1)*10)

        # проверка: вывод фактического url, отправленного поисковику
        # print(url)

        page = requests.get(url)
        # page = requests.get('https://www.yandex.ru/404')  # проверочная ссылка, чтобы получить page.status_code != 200
        """
        print("========================")
        print("Текущая кодировка: " + page.encoding)
        # page.encoding = 'utf-8'
        print(page.headers)
        print("========================")
        """
        if page.status_code != 200:
            print(page.status_code)

        else:
            soup = BeautifulSoup(page.content, "html.parser")  # html.parser встроен в Python
            # print(soup.prettify())

            # ищем на html-странице soup все тэги <h3> (заголовки наших поисковых ссылок)
            link_name = soup.findAll("h3")

            for link_name in link_name:
                # находим родительский тэг <a> для <h3> и вытаскиваем из него ссылку:
                link_object = get_link(str(link_name.find_parent("a")))

                # вывод на печать значений != None:
                if any(link_object) and any(link_name):
                    print(link_object + " " + link_name.text)



def main():
    # читаем из ini-файла:
    start = read_ini("Text/set.ini", 1)  # номер "стартовой" строки
    ms    = read_ini("Text/set.ini", 2)  # интервал опроса
    pages = read_ini("Text/set.ini", 3)  # количество запрашиваемых страниц поиска

    # проверка:
    # print("Стартовая строка:", start)

    path = Path("Text", "queries.txt")

    # подсчёт кол-ва строк в файле queries.txt:
    line_count = sum(1 for lines in open(path))

    # проверка:
    # print("Количество строк в файле:", line_count)

    # бесконечный цикл:
    while True:
        try:
            current = 0

            with open("Text/queries.txt", "r", encoding="utf-8") as file1:
                for line in file1:
                    current += 1

                    if current < start:
                        continue
                    else:
                        print("========================")
                        print(line.strip())
                        print("========================")

                        # здесь запускаем функцию parsing
                        parsing(line, pages)

                    # ждём секунду:
                    wait(ms)

                # следующий цикл считывания начинаемс первой строки:
                start = 1

        # обрабатываем исключение прерывания "Stop" или "Ctrl-C":
        except KeyboardInterrupt:
            # проверка: выводим место остановки ("текущую" строку):
            print("Текущая строка:", current)

            # записываем в .ini "стартовую" строку для следующего запуска:
            write_ini("Text/set.ini", 1, current + 1)

            # завершаем процесс:
            quit()


if __name__ == "__main__":
    main()
    # parsing("python", 1)





