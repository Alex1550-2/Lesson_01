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
    # добавить примеры исходных строк

    # !!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!

    a = temp_string.find("http")
    b = temp_string.find("&amp")

    if a == -1 or b == -1:
        return ""

    temp_string = temp_string[a:b]
    return temp_string


def parsing(line, iters):
    allHeader3  = []  # список для заголовков <h3>
    allLinks    = []  # список для тэгов ссылок <а>

    # переименовать переменные !!!!!
    # links_name


    for i in range(1, iters+1):
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
            soup = BeautifulSoup(page.text, "html.parser")  # html.parser встроен в Python
            # print(soup.prettify())

            # ищем на html-странице soup все тэги <h3> (заголовки наших поисковых ссылок)
            allHeader3 = soup.findAll("h3")

            for i in range(0, len(allHeader3)):
                # создаём пустой элемент списка ссылок:
                allLinks.append(i)

                # ищем родителя для тэга:
                # функция "текст.find_parents(аргумент)": ищем родителя для тэга <h3> (массив allHeader3) с названием 'а':
                # "текст" для функции поиска родителя ищем в html-странице soup с помощью функции find(аргумент)
                # temp_string = soup.find(string=allHeader3[i].get_text()) -> здесь выбираем "текст"
                # allLinks[i] = temp_string.find_parents('a')              -> а здесь ищем родителя для тэга с выбранным ранее текстом
                allLinks[i] = soup.find(string=allHeader3[i].get_text()).find_parent("a")

                allLinks.append(i) = ....


                # проверка: вывод необработанной ссылки, чтобы отлавливать баги:
                # print(allLinks[i])

                # вытаскиваем из строки ссылку:
                allLinks[i] = get_link(str(allLinks[i]))

                # вывод на печать только значений != None:
                if any(allLinks[i]) and any(allHeader3[i]):
                    print(allLinks[i] + " " + allHeader3[i].text)



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
                        parsing(line, iters)

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

    # parsing("tests", 2)
    # parsing('python')
    # parsing()




