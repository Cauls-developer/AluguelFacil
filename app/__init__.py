from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configurar o login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    # Importar e registrar blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Configurar manipuladores de erros personalizados
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Importar modelos para que o Migrate possa detectá-los
    from app import models

    return app

# Importar modelos no final para evitar importações circulares
from app import models