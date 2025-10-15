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
    contratos = relationship("Contrato", back_populates="inquilino")  # NOVO: relação com contratos
    
    def __repr__(self):
        return f"<Inquilino(id={self.id}, nome='{self.nome_completo}', cpf='{self.cpf}')>"
    
    @property
    def tem_contrato_ativo(self):
        """Verifica se o inquilino tem algum contrato ativo"""
        if not hasattr(self, 'contratos') or not self.contratos:
            return False
        return any(c.ativo == 1 for c in self.contratos)
    
    def to_dict(self, include_contratos=False):
        """Converte o objeto para dicionário"""
        data = {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'telefone': self.telefone,
            'nome_fiador': self.nome_fiador
        }
        
        if include_contratos:
            data['contratos'] = [c.to_dict() for c in self.contratos]
        
        return data