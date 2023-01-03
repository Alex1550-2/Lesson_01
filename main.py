"""
This is for copy
"""

import time  # import - инстукция, подключающая модуль из стандартной библиотеки
import json
import keyboard
from pathlib import Path


def Wait(ms):
    n = ms // 50                                # 50 мс - это гарантированных два-три нажатия на клавишу
    for i in range(n):
        time.sleep(0.05)
        if keyboard.is_pressed('q'):            # здесь любое действие программы на прерывание sleep
            print('You Pressed q Key!')

def main():
    with open("Text/data.json", 'r') as f:
        data = f.read()
        start = json.loads(data)

    print("Стартовая строка:", start)

    path = Path("Text", "queries.txt")
    # line_count = sum(1 for lines in open("Text/queries_for_test.txt"))
    line_count = sum(1 for lines in open(path))                     # подсчёт кол-ва строк в файле

    print("Количество строк в файле:", line_count)                  # проверка

    while True:                                                     # бесконечный цикл
        try:
            file1 = open("Text/queries.txt", "r", encoding="utf-8")

            current = 0

            for line in file1:
                current += 1

                if current < start:
                    continue
                else:
                    print(line.strip())

                Wait(1000)

            file1.close                                             # закрываем файл
            start = 1

        except KeyboardInterrupt:                                   # Обработать исключение Ctrl-C
            start = current + 1                                     # нужна следующая строка ( + 1 )

            with open("Text/data.json", 'w') as f:
                json.dump(start, f)
            print("Текущая строка:", current)                       # проверка

            quit()

main()
