"""скрипт для записи поисковых запросов для бесконечного цикла
из файла const.QUERIES_TXT в теблицу settings_cycle (класс Req) БД

в скрипт встроена полная очистка таблицы 'google_req'
и сброс autoincrement счётчика id на начальное значение =1"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from app import create_app  # импортируем из папки app
from app.models import Req, db  # импортируем из папки app
from main_txt import get_file_name

app_db = create_app()  # это 'приложение' для работы с БД


def script_request_db():
    """тело скрипта:"""
    print("работает скрипт script_request_db.py")

    # очищаем содержимое таблицы 'google_req' класса Req:
    with app_db.app_context():
        try:
            db.session.query(Req).delete()

            # сброс счётчика autoincrement id на единицу:
            # ALTER SEQUENCE <tablename>_<id>_seq RESTART WITH 1
            db.session.execute(text("ALTER SEQUENCE google_req_id_seq RESTART WITH 1;"))

            db.session.commit()  # нужен только при актуализации новой информации

            print("таблица 'google_req' БД очищена, google_req_id_seq сброшен")

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка очистки таблицы 'google_req' БД")

    # определяем абсолютные имена текстовых файлов из const.py:
    file_names_tuple = get_file_name()
    file_name_queries_txt = file_names_tuple[1]

    with open(file_name_queries_txt, "r", encoding="utf-8") as file1:
        contents = file1.readlines()

        for new_queries in contents:
            with app_db.app_context():
                try:
                    # удаляем перенос строки "\n":
                    new_queries = new_queries.replace("\n", "")
                    # удаляем перевод курсора в начало "\r":
                    new_queries = new_queries.replace("\r", "")

                    value = Req(request_text=new_queries, status="not_work")

                    db.session.add(value)
                    db.session.commit()  # нужен только при актуализации новой информации

                    print("новая запись в БД: " + new_queries)

                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка записи в БД: " + new_queries)

    print("script_request_db.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_request_db()
