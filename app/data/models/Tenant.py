from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.data.database.base import Base


class Inquilino(Base):
    """Modelo de dados para Inquilinos"""
    
    __tablename__ = 'inquilinos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(200), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(15), nullable=False)
    nome_fiador = Column(String(200), nullable=True)
    
    # Relacionamentos
    casa = relationship("Casa", back_populates="inquilino_atual", uselist=False)
    
    def __repr__(self):
        return f"<Inquilino(id={self.id}, nome='{self.nome_completo}', cpf='{self.cpf}')>"
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'telefone': self.telefone,
            'nome_fiador': self.nome_fiador
        }
