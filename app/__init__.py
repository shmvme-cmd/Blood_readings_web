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

        # Таблица user
        user_cols = [c['name'] for c in inspector.get_columns('user')]
        if 'is_admin' not in user_cols:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0'))
            conn.commit()
        if 'height' not in user_cols:
            conn.execute(text('ALTER TABLE user ADD COLUMN height FLOAT'))
            conn.commit()
        if 'gender' not in user_cols:
            conn.execute(text("ALTER TABLE user ADD COLUMN gender VARCHAR(8)"))
            conn.commit()

        # Таблица medical_analysis — новые показатели
        analysis_cols = [c['name'] for c in inspector.get_columns('medical_analysis')]
        new_float_cols = [
            'ferritin', 'insulin', 'homa_ir', 'vitamin_d',
            # Биохимия из PDF 18.03.2026
            'albumin', 'total_protein', 'ggt', 'potassium', 'calcium',
            'sodium', 'phosphorus', 'chloride',
            # Нечипоренко
            'nechiporenko_leukocytes', 'nechiporenko_erythrocytes', 'nechiporenko_cylinders',
        ]
        for col in new_float_cols:
            if col not in analysis_cols:
                conn.execute(text(f'ALTER TABLE medical_analysis ADD COLUMN {col} FLOAT'))
                conn.commit()
        if 'ai_analysis' not in analysis_cols:
            conn.execute(text('ALTER TABLE medical_analysis ADD COLUMN ai_analysis TEXT'))
            conn.commit()

        # Таблица body_measurement — новые замеры тела
        try:
            body_cols = [c['name'] for c in inspector.get_columns('body_measurement')]
            new_body_cols = ['neck', 'forearm', 'wrist', 'thigh', 'shin', 'abdomen', 'chest']
            for col in new_body_cols:
                if col not in body_cols:
                    conn.execute(text(f'ALTER TABLE body_measurement ADD COLUMN {col} FLOAT'))
                    conn.commit()
        except Exception:
            pass  # таблица ещё не существует — создастся через create_all()


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
