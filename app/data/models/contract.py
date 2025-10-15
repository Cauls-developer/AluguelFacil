from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.data.database.base import Base
from datetime import datetime


class Contrato(Base):
    """Modelo de dados para Contratos de Locação"""
    
    __tablename__ = 'contratos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    casa_id = Column(Integer, ForeignKey('casas.id'), nullable=False)
    inquilino_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False)
    
    # Dados do contrato
    valor_aluguel = Column(Float, nullable=False)
    dia_pagamento = Column(Integer, nullable=False)  # 1-31
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    duracao_meses = Column(Integer, nullable=False, default=12)
    
    # Valores de garantia
    valor_caucao = Column(Float, nullable=True)
    valor_seguro_fianca = Column(Float, nullable=True)
    
    # Multas e taxas
    multa_atraso_percentual = Column(Float, default=10.0)  # %
    juros_dia_percentual = Column(Float, default=0.33)  # %
    multa_rescisao_meses = Column(Integer, default=3)  # meses de aluguel
    
    # Status
    ativo = Column(Integer, default=1)  # 1=ativo, 0=encerrado
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    casa = relationship("Casa", back_populates="contratos")
    inquilino = relationship("Inquilino", back_populates="contratos")
    
    def __repr__(self):
        return f"<Contrato(id={self.id}, casa_id={self.casa_id}, inquilino_id={self.inquilino_id}, ativo={self.ativo})>"
    
    @property
    def status_descricao(self):
        """Retorna descrição do status do contrato"""
        hoje = datetime.now().date()
        if not self.ativo:
            return "Encerrado"
        elif hoje > self.data_fim:
            return "Vencido"
        elif hoje < self.data_inicio:
            return "Futuro"
        else:
            return "Vigente"
    
    @property
    def valor_total_garantias(self):
        """Retorna o valor total das garantias (caução + seguro fiança)"""
        caucao = self.valor_caucao or 0
        seguro = self.valor_seguro_fianca or 0
        return caucao + seguro
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'casa_id': self.casa_id,
            'inquilino_id': self.inquilino_id,
            'valor_aluguel': self.valor_aluguel,
            'dia_pagamento': self.dia_pagamento,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'duracao_meses': self.duracao_meses,
            'valor_caucao': self.valor_caucao,
            'valor_seguro_fianca': self.valor_seguro_fianca,
            'multa_atraso_percentual': self.multa_atraso_percentual,
            'juros_dia_percentual': self.juros_dia_percentual,
            'multa_rescisao_meses': self.multa_rescisao_meses,
            'ativo': self.ativo,
            'status_descricao': self.status_descricao,
            'observacoes': self.observacoes
        }