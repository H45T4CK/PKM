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