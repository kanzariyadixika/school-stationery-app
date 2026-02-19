from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    # Translations
    from app.translations import TRANSLATIONS
    
    @app.context_processor
    def inject_globals():
        lang = session.get('lang', 'en')
        def get_text(key):
            return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
        return dict(get_text=get_text, lang=lang)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.student import student_bp
    from app.routes.billing import billing_bp
    from app.routes.stock import stock_bp
    from app.routes.admin import admin_bp
    from app.routes.student_routes import student_panel_bp
    
    # New admin/settings blueprint if needed, or stick to main.
    # Let's add admin routes for Year/Class to main_bp eventually or student_bp.
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(stock_bp, url_prefix='/stock')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_panel_bp, url_prefix='/student')

    return app
