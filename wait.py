
"""
This is for copy
"""

"""
# отслеживание нажатия клавиш клавиатуры:
def print_pressed_keys(e):
    print(e, e.event_type, e.name)

keyboard.hook(print_pressed_keys)
keyboard.wait()
"""

"""
# чтение строк из текстового файла с помощью функции readline            
for current in range(start, line_count + 1):            # нумерация с единицы!
    Wait(1000)
    # time.sleep(1.0)
    # time.sleep(0.05)
    line = file1.readline()
    print(line.strip())
    # print(current, line.strip())                      # проверка
"""

"""
# библиотека requests: 
    import requests
    
    res = requests.get('https://www.google.ru/search?q='+line)  # GET-запрос

    print(res)              # ответ на запрос (?)
    print(res.status_code)  # код статуса 200 == OK
    print(res.headers)      # ответ в виде заголовка?
    print(res.text)         # вывод текстовых данных ответа (просматриваемой страницы)

    # пример запроса GET, чтобы получить ответ != 200:
    res = requests.get('https://www.yandex.ru/404')
"""

"""
# JSON: читаем из файла номер "стартовой" строки ('r' - файл открыт только для чтения):
    with open("Text/data.json", 'r') as f:
        data = f.read()
        start = json.loads(data)
"""

"""
# JSON: записываем ('w') номер стартовой строки в файл:
    with open("Text/data.json", 'w') as f:
        json.dump(current + 1, f)
"""

# file1.seek(0) - переход к началу текстового файла (в скобках номер байта, с которого читаем)

import keyboard
import time

def Wait_test(ms):
    n = ms // 50                                # 50 мс - это гарантированных два-три нажатия на клавишу
    for i in range(n):
        time.sleep(0.05)
        print('step', i)                        # проверка
        if keyboard.is_pressed('q'):            # if key 'q' is pressed
            print('You Pressed q Key!')

if __name__ == "__main__":
    Wait_test(10000)