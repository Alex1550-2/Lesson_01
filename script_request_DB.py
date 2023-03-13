"""скрипт для записи поисковых запросов для бесконечного цикла
из файла txt в теблицу settings_cycle (класс Req) БД"""
from sqlalchemy.exc import SQLAlchemyError

from app.models import db, Req  # импортируем из папки app
from app import create_app      # импортируем из папки app

from main_txt import get_file_name

app_db = create_app()  # это 'приложение' для работы с БД


def script_request_db():
    """тело скрипта:"""
    print("работает скрипт script_request_DB.py")

    # определяем абсолютные имена текстовых файлов из const.py:
    file_names_tuple = get_file_name()
    file_name_queries_txt = file_names_tuple[1]

    with open(file_name_queries_txt, "r", encoding="utf-8") as file1:
        contents = file1.readlines()

        for new_queries in contents:
            with app_db.app_context():
                try:
                    new_queries = new_queries.replace("\n", "")  # удаляем перенос строки "\n"
                    new_queries = new_queries.replace("\r", "")  # удаляем перевод курсора в начало "\r"

                    value = Req(request_text=new_queries)

                    db.session.add(value)
                    db.session.commit()  # нужен только при актуализации новой информации

                    print("новая запись в БД: " + new_queries)

                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка записи в БД: " + new_queries)

    print("script_request_DB.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_request_db()
