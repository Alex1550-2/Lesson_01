"""
Модуль описывает классы таблиц БД

добавить в main после if __name__ == "__main__":
with app.app_context():
    db.create_all()
чтобы "создать" БД для приложения
"""
from app import db


class Req(db.Model):
    """класс Requests (запросы) БД является наследником стандартного класса Model
    primary_key - основной ключ, unique - значение должно быть уникальным"""

    __tablename__ = "google_req"

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )
    request_text = db.Column(db.String(50), unique=True)


    def __repr__(self):
        """«магическая» функция __repr__, которая определяет способ отображения класса в консоли:
        несколько строк БД - это список экземпляров класса Req"""
        return f"<request {self.id} {self.request_text}>"


class Set(db.Model):
    """класс Settings с настройками для бесконечного цикла"""

    __tablename__ = "settings_cycle"

    id = db.Column(db.Integer, primary_key=True)
    start_string = db.Column(db.Integer)        # 5
    wait_interval = db.Column(db.Integer)       # 2000
    search_page_number = db.Column(db.Integer)  # 2


class Result(db.Model):
    """класс Result для записи результатов поиска google
    по ключевым фразам Requests класса Req"""

    __tablename__ = "result_info"

    id = db.Column(db.Integer, primary_key=True)
    id_req = db.Column(db.Integer)  # равно primary_key id из "google_req"
    res_link = db.Column(db.String(5000))
    res_text = db.Column(db.String(5000))
