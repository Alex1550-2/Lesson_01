"""скрипт для записи начальных настроек бесконечного цикла
из файла txt в теблицу settings_cycle (класс Set) БД"""
from sqlalchemy.exc import SQLAlchemyError

from app import create_app  # импортируем из папки app
from app.models import Set, db  # импортируем из папки app
from main_txt import get_file_name, read_ini

app_db = create_app()  # это 'приложение' для работы с БД


def script_settings_db():
    """тело скрипта:"""
    print("работает скрипт script_settings_db.py")

    # определяем абсолютные имена текстовых файлов из const.py:
    file_names_tuple = get_file_name()
    file_name_set_ini = file_names_tuple[0]

    # читаем настройки из ini-файла:
    start_settings = read_ini(file_name_set_ini)

    with app_db.app_context():
        try:
            new_value = db.session.query(Set).filter(Set.id == 1).first()
            if new_value is not None:
                print(
                    f"исходные значения настроек: {new_value.id} {new_value.start_string}"
                    f" {new_value.wait_interval} {new_value.search_page_number}"
                )

                # присваиваем новые значения начальных настроек из кортежа tuple:
                new_value.start_string = start_settings[0]  # номер "стартовой" строки
                new_value.wait_interval = start_settings[1]  # интервал опроса
                new_value.search_page_number = start_settings[
                    2
                ]  # кол-во страниц поиска
            else:
                print("строка id==1 отсутствует в БД")
                new_value = Set(
                    start_string=start_settings[0],
                    wait_interval=start_settings[1],
                    search_page_number=start_settings[2],
                )
                db.session.add(new_value)

            db.session.commit()  # сохраняем изменения

            # проверяем, что изменения сохранены в БД
            new_value = db.session.query(Set).filter(Set.id == 1).first()
            print(
                f"новые значения настроек:    {new_value.id} {new_value.start_string}"
                f" {new_value.wait_interval} {new_value.search_page_number}"
            )
            print("Начальные настройки успешно записаны в БД")

        except SQLAlchemyError:
            db.session.rollback()  # откатить сессию
            print("Ошибка записи начальных натроек в БД")

    print("script_settings_db.py работу закончил")


if __name__ == "__main__":
    # "создаём" БД внутри нашего приложения app
    with app_db.app_context():
        db.create_all()

    script_settings_db()
