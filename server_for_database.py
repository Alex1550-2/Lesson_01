"""сервер для работы с базой данных postgres"""
import sys

import psycopg2  # использую только для тестовых проверок связи
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, Identity
from sqlalchemy.exc import SQLAlchemyError

import const  # мой файл с контанстами


app = Flask(__name__)
"""приложение app отвечает за соединение с БД"""
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:1@localhost:5432/new_db"  # localhost
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Requests(db.Model):  # pylint: disable=too-few-public-methods
    """класс Запросы для БД
    primary_key - основной ключ, unique - значение должно быть уникальным"""
    id = db.Column(
        db.Integer, Identity(always=True), autoincrement=True, primary_key=True, unique=True
    )
    request_text = db.Column(db.String(50), unique=True)

    def __repr__(self):
        """«магическая» функция __repr__, которая определяет способ отображения класса в консоли:"""
        return f"<request {self.id} {self.request_text}>"


@app.route("/")
@app.route("/index")
def index():
    """Это обработка запроса на сервер: вывод стартовой страницы index
    фактически это GET-запрос"""
    server = {"server_name": "server_for_database.py"}
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
    with app.app_context():
        try:
            # определяем макс значение ключа id - current_max_id, чтобы добавить запись 'id+1'
            temp_value = db.func.max(Requests.id)
            current_max_id = db.session.query(temp_value).scalar()

            # костыль от пустой таблицы:
            if current_max_id is None:
                current_max_id = 0

            new_value = Requests(id=current_max_id + 1, request_text=new_queries)

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

        with app.app_context():
            try:
                # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
                content = Requests.query.distinct().order_by(asc(Requests.id)).all()
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

        with app.app_context():
            try:
                db.session.query(Requests).delete()
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

                # проверка primary_key на уникальность:
                if not check_id(primary_key):  # if check_id(primary_key) == False:
                    return (
                        """
                    <center><p><b>"""
                        + new_text_queries
                        + """:</b> Ошибка записи (идентификатор id занят)</p></center>
                    """
                    )

                with app.app_context():
                    try:
                        new_value = Requests(
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
    """Функция проверяет, свободен ли уникальный primary_key - id
    чтобы записать новую строку в БД с этим id"""
    with app.app_context():
        try:
            content = Requests.query.filter_by(id=id_key).all()
            db.session.rollback()  # откатить сессию

            # если нет записей с этим id
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
                with app.app_context():
                    try:
                        content = Requests.query.filter_by(id=primary_key).first()

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
            with app.app_context():
                try:
                    content = Requests.query.filter_by(id=primary_key).first()
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
    """Функция заполняет БД строками из текстового файла"""
    text_file_name = const.QUERIES_TXT

    with open(text_file_name, "r", encoding="utf-8") as file1:
        contents = file1.readlines()

        for current in contents:
            added_new_request(current.strip())
    return """
        <center><p>в БД записаны строки из файла</p></center>
        """


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
    print("my_server: process started")
    from waitress import serve

    serve(app, host="127.0.0.1", port=8000)  # http://127.0.0.1:8000
