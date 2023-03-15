"""
Модуль отвечает за настройки приложения app,
осуществляющее связь с БД postgres
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Создаём приложение app для связи с БД postgres"""
    app = Flask(__name__, template_folder="templates/")

    app.config[
        "SQLALCHEMY_DATABASE_URI"
        ] = "postgresql://postgres:1@localhost:5432/new_db"  # localhost
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # папка для загрузки текстовых файлов

    app.config['SERVER_NAME'] = '127.0.0.1:8000'

    from app import models  # ОЧЕНЬ ВАЖНО импортировать классы таблиц БД
    db.init_app(app)

    migrate.init_app(app, db)

    return app
