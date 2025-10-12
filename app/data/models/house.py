from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database.base import Base


class Casa(Base):
    """Modelo de dados para Casas"""
    
    __tablename__ = 'casas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(300), nullable=False)
    inquilino_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=True)
    
    # Relacionamentos
    inquilino_atual = relationship("Inquilino", back_populates="casa")
    consumos = relationship("Consumo", back_populates="casa", cascade="all, delete-orphan", 
                          order_by="desc(Consumo.ano), desc(Consumo.mes)")
    
    def __repr__(self):
        return f"<Casa(id={self.id}, nome='{self.nome}', endereco='{self.endereco}')>"
    
    def to_dict(self, include_inquilino=False, include_consumos=False):
        """Converte o objeto para dicionário"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'inquilino_id': self.inquilino_id
        }
        
        if include_inquilino and self.inquilino_atual:
            data['inquilino'] = self.inquilino_atual.to_dict()
        
        if include_consumos:
            data['consumos'] = [c.to_dict() for c in self.consumos]
        
        return data
