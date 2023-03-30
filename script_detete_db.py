"""простой скрипт для удаления всех строк из таблицы "result_info" (класс Result) БД
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from app import create_app  # импортируем из папки app
from app.models import Result, db  # импортируем из папки app

app_db = create_app()  # это 'приложение' для работы с БД


def script_delete_db():
    """тело скрипта:"""
    print("работает скрипт script_delete_db.py")

    # очищаем содержимое таблицы 'result_info' класса Result:
    with app_db.app_context():
        try:
            db.session.query(Result).delete()

            # сброс счётчика autoincrement id на единицу:
            # ALTER SEQUENCE <tablename>_<id>_seq RESTART WITH 1
            db.session.execute(
                text("ALTER SEQUENCE result_info_id_seq RESTART WITH 1;")
            )

            db.session.commit()  # нужен только при актуализации новой информации

            print("таблица 'result_info' БД очищена, result_info_id_seq сброшен")

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка очистки таблицы 'result_info' БД")
    print("script_delete_db.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_delete_db()
