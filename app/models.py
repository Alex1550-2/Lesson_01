"""
Модуль описывает классы таблиц БД

добавить в main после if __name__ == "__main__":
with app.app_context():
    db.create_all()
чтобы "создать" БД для приложения
"""
from app import db


class Req(db.Model):  # pylint: disable=too-few-public-methods
    """класс Requests (запросы) БД является наследником стандартного класса Model
    primary_key - основной ключ, unique - значение должно быть уникальным"""

    __tablename__ = "google_req"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_text = db.Column(db.Text, unique=True)
    status = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        """«магическая» функция __repr__, которая определяет способ отображения класса в консоли:
        несколько строк БД - это список экземпляров класса Req"""
        return f"<request {self.id} {self.request_text} {self.status}>"


class Set(db.Model):  # pylint: disable=too-few-public-methods
    """класс Settings с настройками для бесконечного цикла"""

    __tablename__ = "settings_cycle"

    id = db.Column(db.Integer, primary_key=True)
    start_string = db.Column(db.Integer)  # 5
    wait_interval = db.Column(db.Integer)  # 2000
    search_page_number = db.Column(db.Integer)  # 2


class Result(db.Model):  # pylint: disable=too-few-public-methods
    """класс Result для записи результатов поиска google
    по ключевым фразам Requests класса Req"""

    __tablename__ = "result_info"

    id = db.Column(db.Integer, primary_key=True)

    id_req = db.Column(db.Integer, db.ForeignKey(Req.id, ondelete="SET NULL"))
    # равно primary_key id из "google_req"
    # ondelete="SET NULL": дочерние данные устанавливаются в NULL,
    # iq_req из таблицы result_info будет равен None,
    # когда родительские данные c конкретным Req.id удаляются

    request_text = db.Column(db.Text)
    res_link = db.Column(db.Text)
    res_text = db.Column(db.Text)
    # чтобы избежать ошибок БД из-за длины записи
    # db.String(100) заменил на "безразмерный" db.Text
    timestamp = db.Column(db.DateTime)
