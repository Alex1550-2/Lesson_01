import os

import requests

from main_txt import (
    add_new_queries,
    clear_text_file,
    get_all_queries,
    get_file_name,
    get_link,
    read_ini,
    replace_symbol,
)

# mocker.patch("main.get_link", return_value="https://www.python.org/")


def test_get_link():
    """вынимаем ссылку из исходной строки get_link(str)
    и проверяем успешность её открытия по статусу 200"""
    test_link = get_link("xxxhttps://www.ya.ru/&amp")
    print(test_link)
    page = requests.get(test_link)
    assert page.status_code == 200


def test_replace_symbol():
    """Замена символов действительно выполнена:"""
    test_string = replace_symbol("A A.A")
    assert test_string.find(" ") == -1
    assert test_string.find(".") == -1


def test_get_file_name():
    """Файл действительно существует и открывается:"""
    file_names_tuple = get_file_name()
    file_name_set_ini = file_names_tuple[0]
    file_name_queries_txt = file_names_tuple[1]
    # isfile - проверка наличия файла в заданной директории,
    # возвращает True, если файл есть
    assert os.path.isfile(file_name_set_ini)  # assert f(x) == True
    assert os.path.isfile(file_name_queries_txt)


def test_add_new_queries(tmpdir):
    """Добавляем новую строку в файл и проверяем её наличие после записи
    фикстура tmpdir создёт файл "test_file.txt", который используется только для тестов"""
    a_file = tmpdir.join("test_file.txt")
    a_file.write("first-string\nsecond-string\n")  # заполяем текстовый файл

    add_new_queries("new-test-string", a_file)

    lines = a_file.readlines()  # построчно считали файл
    lines = [line.rstrip("\n") for line in lines]  # это лист []
    assert lines[2] == "new-test-string"


def test_get_all_queries(tmpdir):
    """Проверяем наличие всех существующих строк в файле
    фикстура tmpdir создёт файл "test_file.txt", который используется только для тестов"""
    a_file = tmpdir.join("test_file.txt")
    a_file.write("first-string\nsecond-string\n")  # заполяем текстовый файл

    json = get_all_queries(a_file)

    assert json.find("first-string") != -1
    assert json.find("second-string") != -1


def test_clear_text_file(tmpdir):
    """Проверяем наличие всех существующих строк в файле
    фикстура tmpdir создёт файл "test_file.txt", который используется только для тестов"""
    a_file = tmpdir.join("test_file.txt")
    a_file.write("first-string\nsecond-string\n")  # заполяем текстовый файл

    clear_text_file(a_file)

    assert len(a_file.read()) == 0


def test_read_ini():
    """Проверяем чтение конфигурационных параметров из файла .ini
    специально для тестов создан файл set_test.ini - копия боевого файла settings.ini"""
    start_settings = read_ini(
        "C:\\Users\\user\\PycharmProjects\\Lesson_01\\tests\\set_test.ini"
    )
    print(start_settings)
    assert start_settings[0] == 2
    assert start_settings[1] == 2000
    assert start_settings[2] == 2

    # mock_file = Mock()
    # mock_file.name = "test_set.ini"
    # mock_file.__iter__.return_value = {"start_string": 10, "wait_interval": 2000, "search_page_number": 1}
    #
    # start_settings = read_ini(mock_file.name)
    #
    # assert start_settings[0] == 10

    """#read_ini():
    file_name = replace_symbol(os.path.abspath(os.path.join(this_dir(), os.pardir)) + "/" + set_ini)
    test_start_settings = read_ini(file_name)
    assert test_start_settings[1] == 2000
    """
