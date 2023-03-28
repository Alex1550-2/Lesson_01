"""скрипт изменяет статус всех запросов из таблицы "google_rec"
(класс Req) БД на значение "not_work"
это служебный скрипт, который работает с "зависшими" запросами
"""
import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from app import create_app  # импортируем из папки app
from app.models import Req, db  # импортируем из папки app
from main_txt import wait

app_db = create_app()  # это 'приложение' для работы с БД


def script_status_db():
    """тело скрипта:"""
    print("работает скрипт script_status_db.py")
    with app_db.app_context():
        try:
            # выборка всех "зависших" запросов со статусом "work":
            content = Req.query.filter(Req.status == "work").all()
            db.session.flush()  # сброс сессии

            for current in content:
                # для лога:
                date_time = dt.datetime.now().isoformat()

                # изменяем статус запроса в таблице "google_req" БД (класс Req)
                # было "work" -> стало "not_work":
                current.status = "not_work"
                current.timestamp = date_time
                db.session.commit()  # нужен только при актуализации новой информации

                print(
                    date_time
                    + " status изменён на 'not_work': "
                    + str(current.id)
                    + " "
                    + current.request_text
                )

                # ждём секунду:
                wait(200)

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка работы скрипта script_status_db.py")
    print("script_status_db.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_status_db()
