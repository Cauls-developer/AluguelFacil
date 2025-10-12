from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DatabaseConfig:
    """Configuração centralizada do banco de dados"""
    
    def __init__(self, database_url='sqlite:///casas_consumo.db', echo=False):
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """Inicializa o engine e cria as tabelas"""
        self.engine = create_engine(self.database_url, echo=self.echo)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        return self.engine
    
    def get_session(self):
        """Retorna uma nova sessão"""
        if not self.SessionLocal:
            raise RuntimeError("Database não inicializado. Execute initialize() primeiro.")
        return self.SessionLocal()
