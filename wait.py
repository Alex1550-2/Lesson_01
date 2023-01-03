
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


Wait_test(10000)