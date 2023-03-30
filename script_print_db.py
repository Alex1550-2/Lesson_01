"""скрипт для печати содержимого теблицы result_info (класс Result) БД"""
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError

from app import create_app  # импортируем из папки app
from app.models import Result, db  # импортируем из папки app

app_db = create_app()  # это 'приложение' для работы с БД


def script_print_db():
    """тело скрипта:"""
    print("работает скрипт script_print_db.py")
    with app_db.app_context():
        try:
            # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
            content = Result.query.distinct().order_by(asc(Result.id)).all()
            db.session.flush()  # сброс сессии
        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка чтения из БД")
    for current in content:
        print(
            str(current.id)
            + " "
            + str(current.id_req)
            + " "
            + current.request_text
            + " "
            + current.res_link
            + " "
            + current.res_text
            + " "
            + str(current.timestamp)
        )
    print("script_print_db.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_print_db()
