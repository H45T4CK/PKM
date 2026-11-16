from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.json.provider import DefaultJSONProvider
from app.config import Config

db = SQLAlchemy()

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if hasattr(obj, 'to_dict') and callable(obj.to_dict):
            return obj.to_dict()
        return super().default(obj)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json = CustomJSONProvider(app)

    # Filter Jinja Tanggal Format DD/MM/YYYY
    def date_dmy_filter(val):
        if not val:
            return "-"
        val_str = str(val).strip()
        if len(val_str) >= 10 and val_str[4] == '-' and val_str[7] == '-':
            try:
                y = val_str[0:4]
                m = val_str[5:7]
                d = val_str[8:10]
                return f"{d}/{m}/{y}"
            except Exception:
                pass
        return val_str

    app.jinja_env.filters['date_dmy'] = date_dmy_filter

    # Context Processor: Tahun Ajaran & Semester Dinamis ke Seluruh Template
    @app.context_processor
    def inject_tahun_ajaran():
        from app.models.user import AppSetting
        ta = AppSetting.get_val('tahun_ajaran', '2026/2027')
        sem = AppSetting.get_val('semester', 'Ganjil')
        return dict(
            tahun_ajaran=ta,
            semester=sem,
            tahun_ajaran_full=f"Tahun Ajaran {ta} – Semester {sem}"
        )

    db.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.guru import guru_bp
    from app.routes.ortu import ortu_bp
    from app.routes.export import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(guru_bp)
    app.register_blueprint(ortu_bp)
    app.register_blueprint(export_bp)

    with app.app_context():
        from app.utils.seeder import init_db_and_seed
        init_db_and_seed()

    return app