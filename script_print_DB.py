"""скрипт для печати содержимого теблицы result_info (класс Result) БД"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc

from app.models import db, Result   # импортируем из папки app
from app import create_app          # импортируем из папки app

app_db = create_app()  # это 'приложение' для работы с БД


def script_print_db():
    with app_db.app_context():
        try:
            # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
            content = Result.query.distinct().order_by(asc(Result.id)).all()
            db.session.flush()  # сброс сессии
        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка чтения из БД")
    for current in content:
        print(str(current.id) + " " + str(current.id_req) + " " + current.res_link + " " + current.res_text)


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_print_db()
