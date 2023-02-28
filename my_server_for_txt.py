"""сервер для работы с текстовым файлом"""
from pathlib import Path

from flask import Flask, render_template, request

import const  # мой файл с контанстами
from main import add_new_queries, clear_text_file, get_all_queries

app = Flask(__name__)
"""app = Flask(__name__, template_folder=template_dir)
по умолчанию template_folder='templates' и её можно не указывать"""


@app.route("/")
@app.route("/index")
def index():
    """Это обработка запроса на сервер: вывод стартовой страницы index
    фактически это GET-запрос"""
    server = {"server_name": "my_server_for_txt.py"}
    return render_template("index.html", server=server)
    # return render_template("index.html")


@app.route("/queries", methods=["POST"])
def process_json():
    """Это обработка POST-запроса на сервер: добавить новую строку в файл
    POST-запрос содержит json формата 'new_queries': 'значение новой строки'"""
    if request.method == "POST":
        print(request)  # <Request 'http://127.0.0.1:5080/queries' [POST]>
        content_type = request.headers.get("Content-Type")
        if content_type == "application/json":
            json = request.json
            print(json)  # пример получаемого json: {'new_queries': 'new_text_queries'}
            new_queries = json["new_queries"]
            file_name_queries_txt = str(
                Path(__file__).resolve(strict=True).parent / const.QUERIES_TXT
            )
            if add_new_queries(new_queries, file_name_queries_txt) is True:
                return (
                    """
                    <center><p><b>"""
                    + new_queries
                    + """:</b> Новый запрос успешно записан в файл</p></center>
                    """
                )
            else:
                return """
                    <p>Ошибка записи нового запроса</p>"""
        else:
            return "Content-Type not supported!"


@app.route("/queries", methods=["GET"])
def get_process():
    """Это обработка "пустого" GET-запроса на сервер: вернуть все строки из файла"""
    if request.method == "GET":
        print(request)  # <Request 'http://127.0.0.1:5080/queries' [GET]>

        file_name_queries_txt = str(
            Path(__file__).resolve(strict=True).parent / const.QUERIES_TXT
        )
        content = get_all_queries(file_name_queries_txt)
        return (
            """
            <p>"""
            + content
            + """</p>"""
        )


@app.route("/queries", methods=["DELETE"])
def delete_all_process():
    """Это обработка DELETE-запроса на сервер: удалить все строки из файла"""
    if request.method == "DELETE":
        print(request)  # <Request 'http://127.0.0.1:5080/queries' [DELETE]>
        file_name_queries_txt = str(
            Path(__file__).resolve(strict=True).parent / const.QUERIES_TXT
        )
        clear_text_file(file_name_queries_txt)
        return """
            <p>Выполнена очистка текстового файла</p>"""


if __name__ == "__main__":
    """http://127.0.0.1:5080 ссылка для браузера"""
    print("my_server: process started")
    from waitress import serve

    serve(app, host="127.0.0.1", port=5080)
