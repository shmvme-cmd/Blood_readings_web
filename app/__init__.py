from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap5()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.auth import auth_bp
    from app.routes import main_bp
    from app.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _migrate_db()
        _create_default_user()

    return app


def _migrate_db():
    """Добавляет колонки, которых нет в существующих таблицах."""
    from sqlalchemy import inspect, text
    with db.engine.connect() as conn:
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('user')]
        if 'is_admin' not in cols:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0'))
            conn.commit()


def _create_default_user():
    from app.models import User
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    elif not admin.is_admin:
        admin.is_admin = True
        db.session.commit()
