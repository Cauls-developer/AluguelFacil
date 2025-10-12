from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database.base import Base



class Consumo(Base):
    """Modelo de dados para Consumo mensal"""
    
    __tablename__ = 'consumos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    casa_id = Column(Integer, ForeignKey('casas.id'), nullable=False)
    
    # Dados temporais
    mes = Column(Integer, nullable=False)  # 1-12
    ano = Column(Integer, nullable=False)
    
    # Dados de consumo
    consumo_mes_anterior = Column(Float, nullable=False, default=0.0)
    consumo_mes_atual = Column(Float, nullable=False)
    valor_conta = Column(Float, nullable=False)
    consumo_individual_proporcional = Column(Float, nullable=True)
    
    # Relacionamento
    casa = relationship("Casa", back_populates="consumos")
    
    def __repr__(self):
        return f"<Consumo(id={self.id}, casa_id={self.casa_id}, mes={self.mes}/{self.ano})>"
    
    @property
    def consumo_diferenca(self):
        """Calcula a diferença de consumo entre o mês atual e anterior"""
        return self.consumo_mes_atual - self.consumo_mes_anterior
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'casa_id': self.casa_id,
            'mes': self.mes,
            'ano': self.ano,
            'consumo_mes_anterior': self.consumo_mes_anterior,
            'consumo_mes_atual': self.consumo_mes_atual,
            'valor_conta': self.valor_conta,
            'consumo_individual_proporcional': self.consumo_individual_proporcional,
            'consumo_diferenca': self.consumo_diferenca
        }
