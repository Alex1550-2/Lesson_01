"""проект: starter.py + worker.py + saver.py
"трёх-процессный аналог "main_DB" с использованием очереди RabbitMQ
бесконечный цикл чтения строк из БД
запись результатов в БД и print, front отсутствует
"""

import json
import sys
from datetime import datetime

import pika
from sqlalchemy.exc import SQLAlchemyError

from app import create_app  # импортируем из папки app
from app.models import Req, Result, db  # импортируем из папки app
from main_txt import wait

app_db = create_app()  # это 'приложение' для работы с БД


def callback(channel, method, _, body):
    """пример json на входе из очереди 'result_queue':
    {'id_req': '2', 'request_text': 'закладка GBL в челик',
    'res_link': 'link_object1', 'res_text': 'link_text1'}
    получение запроса из очереди 'result_queue' RabbitMQ
    запись результатов парсинга в таблицу "result_info" БД
    изменение статуса запроса в таблице "google_req" БД

    в оригинале вместо "_" аргумент properties
    """
    # отправка подтверждающего сообщения со стороны worker, что сообщение получено:
    channel.basic_ack(delivery_tag=method.delivery_tag)

    # формируем исходный json из сообщения из очереди:
    source_dict = json.loads(body)

    # для лога:
    date_time = datetime.now().isoformat()
    print(date_time + " saver receive:< " + str(source_dict))

    # записываем принятые данные в таблицу "result_info" БД (класс Result):
    with app_db.app_context():
        try:
            new_value = Result(
                id_req=source_dict["id_req"],  # равно primary_key id из "google_req"
                request_text=source_dict["request_text"],
                res_link=source_dict["res_link"],
                res_text=source_dict["res_text"],
                timestamp=date_time,
            )
            db.session.add(new_value)
            db.session.commit()  # нужен только при актуализации новой информации

            # для лога:
            date_time = datetime.now().isoformat()
            print(date_time + " saved in DB: " + str(source_dict))

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Скрипт saver.py: ошибка записи в БД")
            # завершаем процесс:
            sys.exit()

    # изменяем статус запроса в таблице "google_req" БД (класс Req)
    # было "work" -> стало "not_work":
    with app_db.app_context():
        try:
            # поиск записи по primary_key 'id' в таблице "google_req" БД (класс Req):
            content = Req.query.filter(Req.id == int(source_dict["id_req"])).first()

            content.status = "not_work"
            content.timestamp = date_time
            db.session.commit()  # нужен только при актуализации новой информации

            # для лога:
            date_time = datetime.now().isoformat()
            print(date_time + " status changed in DB: " + str(source_dict))

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Скрипт saver.py: ошибка изменения статуса в БД")
            # завершаем процесс:
            sys.exit()

    # ждём 200 ms
    wait(200)


def main():
    """получение запроса из очереди 'result_queue' RabbitMQ
    запись результатов парсинга в таблицу "result_info" БД
    изменение статуса запроса в таблице "google_req" БД
    вся обработка в функции callback'"""

    # подключение к брокеру сообщений, находящемуся на локальном хосте:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # метод создаёт "биржу" exchange или проверяет существующую:
    channel.exchange_declare(exchange="Lesson_01", exchange_type="topic")

    # создание очереди сообщений, название очереди параметр queue,
    # "устойчивость" durable - защита от перезагрузки сервера RabbitMQ:
    channel.queue_declare(queue="result_queue", durable=True)

    # привязываем очередь queue='result_queue' к бирже exchange='Lesson_01'
    channel.queue_bind("result_queue", "Lesson_01", routing_key="result")

    # RabbitMQ единовременно отправляет только одно сообщение worker-у
    # из очереди и ждёт, когда worker освободится:
    channel.basic_qos(prefetch_count=1)

    # бесконечный цикл:
    while True:
        try:
            channel.basic_consume(on_message_callback=callback, queue="result_queue")
            channel.start_consuming()

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
