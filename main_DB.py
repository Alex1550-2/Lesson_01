"""скрипт: бесконечный цикл чтения строк из БД
запись результатов в БД и print, front отсутствует
"""
import sys
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError

from main_txt import wait, parsing

from app.models import db, Req, Set, Result     # импортируем из папки app
from app import create_app                      # импортируем из папки app

app_db = create_app()  # это 'приложение' для работы с БД


def main():
    """скрипт: бесконечный цикл чтения строк из БД>"""
    # определяем значения начальных настроек:
    with app_db.app_context():
        try:
            value = db.session.query(Set).filter(Set.id == 1).first()
            if value is not None:
                print(f"значения начальных настроек: {value.id} {value.start_string}"
                      f" {value.wait_interval} {value.search_page_number}")
                start = value.start_string          # номер "стартовой" строки
                wait_ms = value.wait_interval       # интервал опроса
                pages = value.search_page_number    # количество запрашиваемых страниц поиска
            else:
                print("Начальные натройки отсутствуют в БД")
                # завершаем процесс:
                sys.exit()

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка чтения начальных натроек в БД")
            # завершаем процесс:
            sys.exit()

    current = 0  # номер итерации в цикле

    # бесконечный цикл:
    while True:
        try:
            # считываем все запросы Request из БД:
            with app_db.app_context():
                try:
                    # выборка с сортировкой по primary_key 'id' по возрастанию 'asc':
                    content = Req.query.distinct().order_by(asc(Req.id)).all()

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
                dictionary_list = parsing(content[current].request_text, pages)

                # записываем в таблицу result_info БД результаты поиска:
                for len_list in range(0, len(dictionary_list)):
                    with app_db.app_context():
                        try:
                            new_value = Result(
                                id_req=current+1,  # равно primary_key id из "google_req" ?
                                res_link=dictionary_list[len_list]["link"],
                                res_text=dictionary_list[len_list]["text"]
                                )
                            db.session.add(new_value)
                            db.session.commit()  # нужен только при актуализации новой информации

                            print(dictionary_list[len_list]["link"] + " " + dictionary_list[len_list]["text"])

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
                        new_value.start_string = current+2  # номер "стартовой" строки
                        db.session.commit()  # сохраняем изменения

                        # проверка:
                        print("будущая строка: " + str(current+2))

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
