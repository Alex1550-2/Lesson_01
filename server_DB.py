"""сервер для работы с базой данных postgres
здесь только 'вьюхи',
остальное выведено в models.py и __init__.py"""


import sys
import os
import flask

import psycopg2  # использую только для тестовых проверок связи
from sqlalchemy import asc
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

import const  # мой файл с контанстами

from flask import render_template, request
from flask import make_response

from app.models import db, Req, Result  # импортируем из папки app
from app import create_app              # импортируем из папки app

from flask import Flask


app = Flask(__name__)  # это 'приложение' для работы с front-end
app_db = create_app()  # это 'приложение' для работы с БД


"""для функции upload_file:"""
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # ограничение на загрузку .txt - 1 МБ
app.config['UPLOAD_EXTENSIONS'] = ['.txt']


@app.route("/")
@app.route("/index")
def index():
    """Это обработка запроса на сервер: вывод стартовой страницы index
    фактически это GET-запрос"""
    server = {"server_name": "server_DB.py"}
    return render_template("index_DB.html", server=server)


@app.route("/queries", methods=["POST"])
def process_json():
    """Это обработка POST-запроса на сервер: добавить новую строку в БД
    POST-запрос содержит json формата 'new_queries': 'значение новой строки'"""
    if request.method == "POST":
        print(request)  # <Request 'http://127.0.0.1:8000/queries' [POST]>
        content_type = request.headers.get("Content-Type")
        if content_type == "application/json":
            try:
                json = request.json
                print(
                    json
                )  # пример получаемого json: {'new_queries': 'new_text_queries'}

                new_queries = str(json["new_queries"])

                # запись новой строки в БД выведена в отдельную функцию:
                answer = added_new_request(new_queries)
                return answer

            except SQLAlchemyError:
                return "Ошибка добавления в БД"
        else:
            return "Content-Type not supported!"
    else:
        return "Request.method not supported!"


def added_new_request(new_queries: str) -> str:
    """Функция записывает новую строку в БД
    генерация primary_key id автоматическая"""
    with app_db.app_context():
        try:
            # определяем макс значение ключа id - current_max_id, чтобы добавить запись 'id+1'
            # temp_value = db.func.max(Req.id)
            # current_max_id = db.session.query(temp_value).scalar()

            new_value = Req(request_text=new_queries)

            db.session.add(new_value)
            db.session.commit()  # нужен только при актуализации новой информации
            return (
                    """
                <center><p><b>"""
                    + new_queries
                    + """:</b> Новый запрос успешно записан в БД</p></center>
               """
            )
        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка записи в БД")
            return (
                    """
                <center><p><b>"""
                    + new_queries
                    + """:</b>Ошибка записи в БД</p></center>
                """
            )


@app.route("/queries", methods=["GET"])
def get_process():
    """Это обработка "пустого" GET-запроса на сервер: вернуть все строки из БД"""
    if request.method == "GET":
        print(request)  # <Request 'http://127.0.0.1:8000/queries' [GET]>

        with app_db.app_context():
            try:
                # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
                content = Req.query.distinct().order_by(asc(Req.id)).all()
                db.session.flush()  # сброс сессии
                return convert_var_for_html(content)
            except SQLAlchemyError:
                db.session.rollback()  # откатить сессию
                return "Ошибка чтения из БД"
    else:
        return "Request.method not supported!"


def convert_var_for_html(content) -> str:
    """ответ на запрос '/queries' - вывод data для html в отдельную функцию"""
    string_for_html: str = ""

    if len(content) != 0:
        for req in content:
            string_for_html += "<p>" + str(req.id) + ": " + req.request_text + "</p>"
    else:
        string_for_html = "<p>нет записей в БД</p>"
    return string_for_html


@app.route("/delete", methods=["DELETE"])
def delete_all():
    """Это обработка DELETE-запроса на сервер: удалить ВСЕ строки из БД"""
    if request.method == "DELETE":
        print(request)  # <Request 'http://127.0.0.1:8000/delete' [DELETE]>

        with app_db.app_context():
            try:
                db.session.query(Req).delete()
                # сброс счётчика autoincrement id на единицу:
                # ALTER SEQUENCE <tablename>_<id>_seq RESTART WITH 1
                db.session.execute(text("ALTER SEQUENCE google_req_id_seq RESTART WITH 1;"))

                db.session.query(Result).delete()
                # сброс счётчика autoincrement id на единицу:
                # ALTER SEQUENCE <tablename>_<id>_seq RESTART WITH 1
                db.session.execute(text("ALTER SEQUENCE result_info_id_seq RESTART WITH 1;"))

                db.session.commit()
                return """
                    <center><p>Удалены все запросы из таблицы БД</p></center>
                    """
            except SQLAlchemyError:
                db.session.rollback()  # откатить сессию
                print("ошибка очистки ТАБЛИЦЫ БД")
                return """
                    <center><p>Ошибка очистки таблицы БД</p></center>
                    """
    else:
        return "Request.method not supported!"


@app.route("/add_line_id", methods=["POST"])
def add_id_process():
    """Это обработка POST-запроса на сервер: добавить строку в БД по её primary_key"""
    if request.method == "POST":
        print(request)  # <Request 'http://127.0.0.1:8000/delete_line_id' [POST]>

        content_type = request.headers.get("Content-Type")
        if content_type == "application/json":
            try:
                json = request.json
                # пример json: {"primary_key": primary_key.value,
                # "new_text_queries": new_text_queries.value}
                print(json)

                primary_key = int(json["primary_key"])
                new_text_queries = str(json["new_text_queries"])

                # если primary_key найден (return False), то 'поверх' записывать нельзя:
                if not check_id(primary_key):  # if check_id(primary_key) == False:
                    return (
                            """
                    <center><p><b>"""
                            + new_text_queries
                            + """:</b> Ошибка записи (идентификатор id занят)</p></center>
                    """
                    )

                with app_db.app_context():
                    try:
                        new_value = Req(
                            id=primary_key, request_text=new_text_queries
                        )
                        db.session.add(new_value)
                        db.session.commit()  # нужен только при актуализации новой информации
                        return (
                                """
                            <center><p><b>"""
                                + new_text_queries
                                + """:</b> Новый запрос успешно записан в БД</p></center>
                                       """
                        )
                    except SQLAlchemyError:
                        db.session.rollback()  # откатить сессию
                        print("Ошибка записи в БД")
                        return (
                                """
                        <center><p><b>"""
                                + new_text_queries
                                + """:</b>Ошибка записи в БД</p></center>
                        """
                        )
            except SQLAlchemyError:
                return "Ошибка добавления в БД"
        else:
            return "Content-Type not supported!"
    else:
        return "Request.method not supported!"


def check_id(id_key: int) -> bool:
    """Функция проверяет, записан ли в БД уникальный primary_key - id
    чтобы отобразить существующую или записать новую строку в БД с этим id
    Если записей с этим id не найдено, то возвращаем True"""
    with app_db.app_context():
        try:
            content = Req.query.filter_by(id=id_key).all()
            db.session.rollback()  # откатить сессию

            # если нет записей с этим id возвращаем True
            if len(content) == 0:
                return True
            return False
        except SQLAlchemyError:
            print("ошибка запроса id строки в БД")
            return False


@app.route("/delete_line_id", methods=["POST"])
def delete_id_process():
    """Это обработка POST-запроса на сервер: удалить строку из БД по её primary_key"""
    if request.method == "POST":
        print(request)  # <Request 'http://127.0.0.1:8000/delete_line_id' [DELETE]>

        content_type = request.headers.get("Content-Type")
        if content_type == "application/json":
            try:
                json = request.json
                print(json)  # пример получаемого json: {'primary_key': '12'}

                primary_key = str(json["primary_key"])
                with app_db.app_context():
                    try:
                        content = Req.query.filter_by(id=primary_key).first()

                        db.session.delete(content)
                        db.session.commit()  # сброс сессии flush() внутри commit()
                        return (
                                """
                            <center><p><b>id """
                                + primary_key
                                + """:</b> Запись удалена из БД</p></center>
                            """
                        )
                    except SQLAlchemyError:
                        db.session.rollback()  # откатить сессию
                        print("Ошибка записи в БД")
                        return (
                                """
                            <center><p><b>id """
                                + primary_key
                                + """:</b>Ошибка удаления из БД</p></center>
                            """
                        )
            except SQLAlchemyError:
                return "Ошибка удаления из БД"
        else:
            return "Content-Type not supported!"
    else:
        return "Request.method not supported!"


@app.route("/show_line_id", methods=["POST"])
def show_id_process():
    """Это обработка POST-запроса на сервер: показать строку из БД по её primary_key"""
    if request.method == "POST":
        print(request)  # <Request 'http://127.0.0.1:8000/delete_line_id' [DELETE]>

        content_type = request.headers.get("Content-Type")
        if content_type == "application/json":
            json = request.json
            print(json)  # пример получаемого json: {'primary_key': '12'}

            primary_key = str(json["primary_key"])

            # если primary_key не найден (return True), то отображать нечего:
            if check_id(int(primary_key)) is True:  # if check_id(primary_key) == False:
                return (
                        """
                    <center><p><b>id """
                        + primary_key
                        + """:</b> Ошибка отображения (идентификатор id отсутствует в БД)</p></center>
                               """
                )

            with app_db.app_context():
                try:
                    content = Req.query.filter_by(id=primary_key).first()
                    db.session.flush()  # сброс сессии
                    return (
                            "<p>" + str(content.id) + ": " + content.request_text + "</p>"
                    )
                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка чтения из БД")
                    return "<p>нет записей в БД</p>"
        else:
            return "Content-Type not supported!"
    else:
        return "Request.method not supported!"


@app.route("/all_add", methods=["GET"])
def all_added():
    """Функция заполняет БД строками из текстового файла const.QUERIES_TXT"""
    text_file_name = const.QUERIES_TXT

    with open(text_file_name, "r", encoding="utf-8") as file1:
        contents = file1.readlines()

        for current in contents:
            added_new_request(current.strip())
    return """
        <center><p>в БД записаны строки из файла</p></center>
        """


@app.route("/", methods=["POST"])
def upload_file():
    """Функция выбирает через проводник текстовый файл,
    заполняет БД его строками
    и сохраняет в папку Text проекта
    установлено ограничение: только .txt файлы не более 1 МБ"""
    uploaded_file = request.files['file']

    filename = uploaded_file.filename  # проверка допустимого расширения
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        flask.abort(401)  # прерываем, если не .txt

    file_contents = uploaded_file.stream.read().decode("utf-8")
    print(file_contents)

    worlds = file_contents.split("\n")  # метод split, сепаратор "\n"

    for current in worlds:
        if current != "":  # защита от пустой строки
            current = current.replace("\r", "")  # удаляем перевод курсора в начало "\r"
            added_new_request(current)

    response = make_response('', 301)
    response.data = "<link rel='icon' href='data:,'><p>Содержимое выбранного текстового файла:</p><p>" + \
                    file_contents + "</p><p>Для возврата перейдите на страницу 'index'</p>"
    return response


# реализация через psycopg2
# connect_db()   # открыли соединение и сразу закрыли
# get_content()  # подключились, печать всей таблицы, закрыли соединение


def connect_db():
    """функция тестового соединения с БД - реализована на psycopg2
    используется для проверки параместров соединения вроде пароля и хоста
    и сразу соединение закрывается"""
    try:
        conn = psycopg2.connect(
            dbname="new_db",
            user="postgres",
            password="1",
            host="localhost",
            port="5432",
        )
        print("Database opened successfully")
        conn.close()  # закрываем соединение
    except psycopg2.Error as error:
        print(error)
        sys.exit()


def get_content():
    """Тестовая функция - реализована на psycopg2
    запрос всех данных из таблицы Request"""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="new_db",
            user="postgres",
            password="1",
            host="localhost",
            port="5432",
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM Requests ORDER BY id")
        print("The number of parts: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            print(row)
            row = cur.fetchone()

        cur.close()
    except psycopg2.Error as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    print("my_server: process started")

    # запускаем наше приложение app
    from waitress import serve  # app(run) не использовать !!!
    serve(app, host="127.0.0.1", port=8000)  # http://127.0.0.1:8000
