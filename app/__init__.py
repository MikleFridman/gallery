import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache

from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
bootstrap = Bootstrap()
csrf = CSRFProtect()
login = LoginManager()
login.login_message = 'Please log in to access this page'
login.login_view = 'login'
cache = Cache()

from app.users import bp as users_bp
from app.gallery import bp as gallery_bp


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)
    cache.init_app(app)
    app.register_blueprint(users_bp)
    app.register_blueprint(gallery_bp)
    return app
