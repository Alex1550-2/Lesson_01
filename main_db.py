"""скрипт: бесконечный цикл чтения строк из БД
запись результатов в БД и print, front отсутствует
"""
import sys
from datetime import datetime

from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError

from app import create_app  # импортируем из папки app
from app.models import Req, Result, Set, db  # импортируем из папки app
from main_txt import parsing, wait
from starter import read_settings

app_db = create_app()  # это 'приложение' для работы с БД


def main():
    """скрипт: бесконечный цикл чтения строк из БД>"""
    # определяем значения начальных настроек:
    start_settings = read_settings()

    # извлекаем из кортежа tuple значения начальных настроек:
    start = start_settings[0]  # номер "стартовой" строки
    wait_ms = start_settings[1]  # интервал опроса
    pages = start_settings[2]  # количество запрашиваемых страниц поиска

    current = 0  # номер итерации в цикле

    # бесконечный цикл:
    while True:
        try:
            # считываем все запросы Request из БД:
            with app_db.app_context():
                try:
                    # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
                    content = Req.query.order_by(asc(Req.id)).all()

                    db.session.flush()  # сброс сессии
                    print(content)

                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка чтения из БД")
                    # завершаем процесс:
                    sys.exit()

            for current in range(start - 1, len(content)):
                print("========================")
                print(content[current].request_text)
                print("========================")

                # форируем список словарей из ссылок и их текстового описания:
                link_list = parsing(content[current].request_text, pages)

                # записываем в таблицу result_info БД результаты поиска:
                for current_link in link_list:
                    # текущее дата-время::
                    date_time = datetime.now().isoformat()

                    with app_db.app_context():
                        try:
                            new_value = Result(
                                id_req=content[
                                    current
                                ].id,  # равно primary_key id из "google_req"
                                request_text=content[current].request_text,
                                res_link=current_link["link"],
                                res_text=current_link["text"],
                                timestamp=date_time,
                            )
                            db.session.add(new_value)
                            db.session.commit()  # нужен только при актуализации новой информации

                            print(current_link["link"] + " " + current_link["text"])

                        except SQLAlchemyError:
                            db.session.rollback()  # откатить сессию
                            print("Ошибка записи в БД")
                            # завершаем процесс:
                            sys.exit()

            # следующий цикл считывания начинаемс первой строки:
            start = 1

            # ждём секунду:
            wait(wait_ms)

        # обрабатываем исключение прерывания "Stop" или "Ctrl-C":
        except KeyboardInterrupt:
            # записываем в БД "стартовую" строку для следующего запуска:
            with app_db.app_context():
                try:
                    new_value = db.session.query(Set).filter(Set.id == 1).first()
                    if new_value is not None:
                        new_value.start_string = current + 2  # номер "стартовой" строки
                        db.session.commit()  # сохраняем изменения

                        # проверка:
                        print("будущая строка: " + str(current + 2))

                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка перезаписи номера стартовой строки в БД")

            # завершаем процесс:
            sys.exit()


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    main()
