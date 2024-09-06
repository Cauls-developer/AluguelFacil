import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Chave secreta para proteção contra CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-nao-use-em-producao'
    
    # Configuração do SQLAlchemy com SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ChaveMestra.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de e-mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['seu-email@exemplo.com']
    
    # Configurações específicas do aplicativo
    CONTAS_POR_PAGINA = 10

class DevelopmentConfig(Config):
    DEBUG = True
    # Usando o mesmo banco de dados ChaveMestra.db para desenvolvimento
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ChaveMestra.db')

class TestingConfig(Config):
    TESTING = True
    # Para testes, usamos um banco de dados em memória
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ProductionConfig(Config):
    # Em produção, usamos o mesmo ChaveMestra.db, mas pode ser substituído por uma variável de ambiente
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ChaveMestra.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}