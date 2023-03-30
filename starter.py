"""проект: starter.py + worker.py + saver.py
"трёх-процессный аналог "main_DB" с использованием очереди RabbitMQ
бесконечный цикл чтения строк из БД
запись результатов в БД и print, front отсутствует
"""
import datetime
import json
import sys

import pika
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import nullsfirst

from app import create_app  # импортируем из папки app
from app.models import Req, Set, db  # импортируем из папки app
from main_txt import wait

app_db = create_app()  # это 'приложение' для работы с БД


def read_settings() -> tuple:
    """определяем начальные настройки из таблицы "settings_cycle" (класс Set)
    единовременно перед началом бесконечного цикла:
    определяем значения начальных настроек:
    """
    with app_db.app_context():
        try:
            value = db.session.query(Set).filter(Set.id == 1).first()
            if value is not None:
                print(
                    f"значения начальных настроек: {value.id} {value.start_string}"
                    f" {value.wait_interval} {value.search_page_number}"
                )
                result = (
                    int(value.start_string),  # start - номер "стартовой" строки
                    int(value.wait_interval),  # wait_ms - интервал опроса
                    int(value.search_page_number),
                )
                # pages - количество запрашиваемых страниц поиска
                return result

            print("Начальные натройки отсутствуют в БД")
            # завершаем процесс:
            sys.exit()

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка чтения начальных натроек в БД")
            # завершаем процесс:
            sys.exit()


def main():
    """скрипт: бесконечный цикл
    читаем строковые запросы из таблицы "google_req" БД
    изменяем статус запроса в таблице "google_req" БД (класс Req)
    и их отправка в очередь 'request_queue' RabbitMQ"""

    # подключение к брокеру сообщений, находящемуся на локальном хосте:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # метод создаёт "биржу" exchange или проверяет существующую:
    channel.exchange_declare(exchange="Lesson_01", exchange_type="topic")

    # создание очереди сообщений, название очереди параметр queue,
    # "устойчивость" durable - защита от перезагрузки сервера RabbitMQ:
    channel.queue_declare(queue="request_queue", durable=True)
    channel.queue_declare(queue="result_queue", durable=True)

    # привязываем очередь queue='request_queue' к бирже exchange='Lesson_01'
    channel.queue_bind("request_queue", "Lesson_01", routing_key="request")
    channel.queue_bind("result_queue", "Lesson_01", routing_key="result")

    # бесконечный цикл:
    while True:
        try:
            # определяем начальные настройки:
            start_settings = read_settings()

            # извлекаем из кортежа tuple значения начальных настроек:
            # start = start_settings[0]  # номер "стартовой" строки
            wait_ms = start_settings[1]  # интервал опроса
            pages = start_settings[2]  # количество запрашиваемых страниц поиска

            # выборка из основной таблицы "google_req" (класс Req):
            with app_db.app_context():
                try:
                    # выборка записей с меткой status "not_work"
                    # с сортировкой по временнОй метке timestamp по возрастанию "asc"
                    # при этом новые записи с отсутствующей временнОй меткой timestamp
                    # будут первыми в выборке (команда nullsfirst):
                    content = (
                        Req.query.filter(Req.status == "not_work")
                        .order_by(nullsfirst(asc(Req.timestamp)))
                        .limit(25)
                        .all()
                    )

                    for current in content:
                        # формируем словарь для отправки в очередь:
                        temp_dict = {
                            "wait": str(wait_ms),
                            "pages": str(pages),
                            "id": str(current.id),
                            "request": current.request_text,
                        }

                        # для лога:
                        date_time = datetime.datetime.now().isoformat()
                        print(
                            date_time
                            + " starter send:> "
                            + temp_dict["wait"]
                            + " "
                            + temp_dict["pages"]
                            + " "
                            + temp_dict["id"]
                            + " "
                            + temp_dict["request"]
                        )

                        # отправили запрос в очередь 'request':
                        channel.basic_publish(
                            exchange="Lesson_01",
                            routing_key="request",
                            body=json.dumps(temp_dict).encode("utf-8"),
                        )

                        # изменяем статус запроса в таблице "google_req" БД (класс Req)
                        # было "not_work" -> стало "work":
                        current.status = "work"
                        current.timestamp = date_time
                        db.session.commit()  # нужен только при актуализации новой информации

                        # ждём секунду:
                        wait(1000)

                except SQLAlchemyError:
                    db.session.rollback()  # откатить сессию
                    print("Ошибка работы скрипта starter.py")
                    # завершаем процесс:
                    sys.exit()

            # для лога:
            date_time = datetime.datetime.now().isoformat()
            print(date_time + " cycle complete")

            # ждём 5 секунд:
            wait(5000)

        # обрабатываем исключение прерывания "Stop" или "Ctrl-C":
        except KeyboardInterrupt:
            # закрываем соединение с брокером сообщений:
            connection.close()

            # завершаем процесс:
            sys.exit()


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    main()
