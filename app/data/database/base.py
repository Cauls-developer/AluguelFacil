from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from pathlib import Path

Base = declarative_base()


class DatabaseConfig:
    """Configuração centralizada do banco de dados"""
    
    def __init__(self, database_url=None, echo=False):
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
        
        # Define o caminho do banco de dados
        if database_url:
            self.database_url = database_url
        else:
            # Usa a pasta de dados do usuário
            self.database_url = self._get_database_path()
    
    def _get_database_path(self):
        """
        Retorna o caminho apropriado para o banco de dados.
        
        - Em desenvolvimento: raiz do projeto
        - Em produção (executável): pasta AppData do usuário
        """
        # Detecta se está rodando como executável PyInstaller
        if getattr(sys, 'frozen', False):
            # Está rodando como executável
            # Usa a pasta AppData do usuário (com permissão de escrita)
            appdata = os.environ.get('APPDATA')  # Windows
            if appdata:
                app_folder = Path(appdata) / 'AluguelFacil'
            else:
                # Fallback para pasta home do usuário
                app_folder = Path.home() / '.aluguel_facil'
            
            # Cria a pasta se não existir
            app_folder.mkdir(parents=True, exist_ok=True)
            
            db_path = app_folder / 'casas_consumo.db'
            print(f"📂 Banco de dados será criado em: {db_path}")
            
        else:
            # Está rodando em desenvolvimento
            # Usa a pasta atual do projeto
            db_path = Path('casas_consumo.db')
        
        return f'sqlite:///{db_path}'
    
    def initialize(self):
        """Inicializa o engine e cria as tabelas"""
        try:
            self.engine = create_engine(self.database_url, echo=self.echo)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine)
            print("✅ Banco de dados inicializado com sucesso!")
            return self.engine
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            print(f"Caminho tentado: {self.database_url}")
            raise
    
    def get_session(self):
        """Retorna uma nova sessão"""
        if not self.SessionLocal:
            raise RuntimeError("Database não inicializado. Execute initialize() primeiro.")
        return self.SessionLocal()
    
    def get_database_location(self):
        """Retorna o caminho completo do arquivo de banco de dados"""
        # Remove o prefixo 'sqlite:///'
        return self.database_url.replace('sqlite:///', '')
