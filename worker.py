"""проект: starter.py + worker.py + saver.py
"трёх-процессный аналог "main_DB" с использованием очереди RabbitMQ
бесконечный цикл чтения строк из БД
запись результатов в БД и print, front отсутствует
"""
import datetime as dt
import json
import sys
from datetime import datetime

import pika

from main_txt import parsing, wait


def callback(channel, method, _, body):
    """пример json на входе из очереди 'request_queue':
    {'wait': '2000', 'pages': '2', 'id': '1', 'request': 'рамп купить закладку болтушка в тула'}
    получение запроса из очереди 'request_queue' RabbitMQ
    парсим google на основании полученного запроса
    отправляем результат парсинга в очередь 'result_queue

    в оригинале вместо "_" аргумент properties
    """
    # отправка подтверждающего сообщения со стороны worker, что сообщение получено:
    channel.basic_ack(delivery_tag=method.delivery_tag)

    # формируем исходный json из сообщения из очереди:
    source_dict = json.loads(body)

    # для лога:
    date_time = datetime.now().isoformat()
    print(date_time + " worker receive:< " + str(source_dict))

    # запрашиваем google и получаем в ответ результаты поиска
    # в виде ссылок и их текстового описания:
    link_list = parsing(source_dict["request"], int(source_dict["pages"]))

    # ждём wait_interval из settings:
    # wait(int(source_dict['wait']))

    for current_link in link_list:
        # формируем исходящий словарь для отправки в очередь:
        outgoing_dict = {
            "id_req": source_dict["id"],
            "request_text": source_dict["request"],
            "res_link": current_link["link"],
            "res_text": current_link["text"],
        }

        # для лога:
        date_time = dt.datetime.now().isoformat()
        print(
            date_time
            + " worker send:> "
            + str(outgoing_dict["id_req"])
            + " "
            + str(outgoing_dict["request_text"])
            + " "
            + str(outgoing_dict["res_link"])
            + " "
            + str(outgoing_dict["res_text"])
        )

        # отправили запрос в очередь:
        channel.basic_publish(
            exchange="Lesson_01", routing_key="result", body=json.dumps(outgoing_dict)
        )

        # ждём 200 ms:
        wait(200)

    print("====================")


def main():
    """получение запроса из очереди 'request_queue' RabbitMQ
    парсим google на основании полученного запроса
    отправляем результат парсинга в очередь 'result_queue
    вся обработка в функции callback'"""

    # подключение к брокеру сообщений, находящемуся на локальном хосте:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # метод создаёт "биржу" exchange или проверяет существующую:
    channel.exchange_declare(exchange="Lesson_01", exchange_type="topic")

    # создание очереди сообщений, название очереди параметр queue,
    # "устойчивость" durable - защита от перезагрузки сервера RabbitMQ:
    channel.queue_declare(queue="request_queue", durable=True)

    # привязываем очередь queue='request_queue' к бирже exchange='Lesson_01'
    channel.queue_bind("request_queue", "Lesson_01", routing_key="request")

    # RabbitMQ единовременно отправляет только одно сообщение worker-у
    # из очереди и ждёт, когда worker освободится:
    channel.basic_qos(prefetch_count=1)

    # бесконечный цикл:
    while True:
        try:
            channel.basic_consume(on_message_callback=callback, queue="request_queue")
            channel.start_consuming()

        # обрабатываем исключение прерывания "Stop" или "Ctrl-C":
        except KeyboardInterrupt:
            # закрываем соединение с брокером сообщений:
            connection.close()

            # завершаем процесс:
            sys.exit()


if __name__ == "__main__":
    # worker с БД не общается!
    main()
