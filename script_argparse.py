"""простой скрипт для печати / удаления всех строк из таблиц
"result_info" (класс Result) или "google_req" (класс Req) БД

скрипт работает только приусловии ввода аргументов,
пример вызова: python script_argparse.py result_info delete

вызов описания аргументов: python script_argparse.py -h
"""
import argparse
import sys

from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from app import create_app  # импортируем из папки app
from app.models import Req, Result, db  # импортируем из папки app

app_db = create_app()  # это 'приложение' для работы с БД


# определяем аргументы скрипта при использовании анализатора argparse:
parser = argparse.ArgumentParser(
    description="Script: print or delete all data from selected table databases"
)
parser.add_argument(
    "tablename", type=str, help="The name of the table to print / delete data"
)
parser.add_argument("command", type=str, help="Strict command: print or delete")
args = parser.parse_args()


def script_argparse():
    """тело скрипта:"""
    print("работает скрипт script_argparse.py")
    print("таблица " + str(args.tablename) + ", команда " + str(args.command))

    # здесь удаляем содержимое выбранной таблицы:
    if args.command == "delete":
        # очищаем содержимое таблицы:
        with app_db.app_context():
            try:
                if args.tablename == "result_info":
                    db.session.query(Result).delete()
                elif args.tablename == "google_req":
                    db.session.query(Req).delete()
                else:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка №1 очистки таблицы '" + args.tablename + "' БД")
                    # завершаем процесс:
                    sys.exit()

                # сброс счётчика autoincrement id на единицу:
                # ALTER SEQUENCE <tablename>_<id>_seq RESTART WITH 1
                db.session.execute(
                    text("ALTER SEQUENCE " + args.tablename + "_id_seq RESTART WITH 1;")
                )

                db.session.commit()  # нужен только при актуализации новой информации

                print(
                    "таблица '"
                    + args.tablename
                    + "' БД очищена, "
                    + args.tablename
                    + "_id_seq сброшен"
                )

            except SQLAlchemyError:
                db.session.rollback()  # откатить сессию
                print("Ошибка №2 очистки таблицы '" + args.tablename + "' БД")

    elif args.command == "print":
        # печатаем содержимое таблицы:
        with app_db.app_context():
            try:
                # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
                if args.tablename == "result_info":
                    content = Result.query.distinct().order_by(asc(Result.id)).all()
                elif args.tablename == "google_req":
                    content = Req.query.distinct().order_by(asc(Req.id)).all()
                else:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка №3 печати таблицы '" + args.tablename + "' БД")
                    # завершаем процесс:
                    sys.exit()

                db.session.flush()  # сброс сессии
            except SQLAlchemyError:
                db.session.rollback()  # откатить сессию
                print("Ошибка №4 чтения из БД")

        if args.tablename == "result_info":
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
        elif args.tablename == "google_req":
            for current in content:
                print(
                    str(current.id)
                    + " "
                    + str(current.request_text)
                    + " "
                    + str(current.status)
                    + " "
                    + str(current.timestamp)
                )

    print("script_argparse.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_argparse()
