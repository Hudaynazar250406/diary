from flask_sqlalchemy import SQLAlchemy

# Единый экземпляр SQLAlchemy на всё приложение.
# Инициализируется без привязки к конкретному app — привязка происходит в create_app()
# через db.init_app(app). Так модели могут импортировать db без циклических импортов.
db = SQLAlchemy()
