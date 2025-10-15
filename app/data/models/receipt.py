from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database.base import Base
from datetime import datetime


class Recibo(Base):
    """Modelo de dados para Recibos de Pagamento"""
    
    __tablename__ = 'recibos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tipo de recibo
    tipo_recibo = Column(String(50), nullable=False)  # 'aluguel', 'energia', 'servico', 'outros'
    
    # Relacionamentos opcionais
    casa_id = Column(Integer, ForeignKey('casas.id'), nullable=True)
    inquilino_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=True)
    
    # Dados do pagador (se não for inquilino cadastrado)
    nome_pagador = Column(String(200), nullable=False)
    cpf_pagador = Column(String(14), nullable=True)
    
    # Dados do recebedor
    nome_recebedor = Column(String(200), nullable=False)
    cpf_recebedor = Column(String(14), nullable=True)
    
    # Valor e descrição
    valor = Column(Float, nullable=False)
    descricao = Column(Text, nullable=False)  # Descrição detalhada do que está sendo pago
    referente_a = Column(String(200), nullable=False)  # "Aluguel ref. Janeiro/2025", "Conta de Luz ref. Fev/2025", etc
    
    # Datas
    data_pagamento = Column(Date, nullable=False)
    data_emissao = Column(Date, nullable=False, default=datetime.now().date)
    
    # Período de referência (opcional)
    mes_referencia = Column(Integer, nullable=True)  # 1-12
    ano_referencia = Column(Integer, nullable=True)
    
    # Forma de pagamento
    forma_pagamento = Column(String(50), nullable=True)  # 'dinheiro', 'pix', 'transferencia', 'cheque'
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    casa = relationship("Casa", foreign_keys=[casa_id])
    inquilino = relationship("Inquilino", foreign_keys=[inquilino_id])
    
    def __repr__(self):
        return f"<Recibo(id={self.id}, tipo='{self.tipo_recibo}', valor={self.valor}, data={self.data_pagamento})>"
    
    @property
    def valor_extenso(self):
        """Retorna o valor por extenso (simplificado)"""
        # Implementação básica - pode ser melhorada
        return self._numero_por_extenso(self.valor)
    
    def _numero_por_extenso(self, valor):
        """Converte número em extenso (simplificado)"""
        partes = str(valor).split('.')
        reais = int(partes[0])
        centavos = int(partes[1]) if len(partes) > 1 and len(partes[1]) > 0 else 0
        
        # Mapeamento básico
        unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
        dezenas = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
        especiais = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
        centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
        
        if reais == 0:
            texto_reais = 'zero reais'
        elif reais < 10:
            texto_reais = f"{unidades[reais]} {'real' if reais == 1 else 'reais'}"
        elif reais < 20:
            texto_reais = f"{especiais[reais - 10]} reais"
        elif reais < 100:
            d = reais // 10
            u = reais % 10
            texto_reais = f"{dezenas[d]}{' e ' + unidades[u] if u > 0 else ''} reais"
        elif reais < 1000:
            c = reais // 100
            resto = reais % 100
            if reais == 100:
                texto_reais = "cem reais"
            elif resto == 0:
                texto_reais = f"{centenas[c]} reais"
            else:
                texto_resto = self._numero_por_extenso(resto).replace(' reais', '').replace(' real', '')
                texto_reais = f"{centenas[c]} e {texto_resto} reais"
        else:
            # Para valores maiores, retorna formato numérico
            texto_reais = f"{reais} reais"
        
        if centavos > 0:
            if centavos < 10:
                texto_centavos = f"{unidades[centavos]} centavo{'s' if centavos > 1 else ''}"
            elif centavos < 20:
                texto_centavos = f"{especiais[centavos - 10]} centavos"
            else:
                d = centavos // 10
                u = centavos % 10
                texto_centavos = f"{dezenas[d]}{' e ' + unidades[u] if u > 0 else ''} centavos"
            
            return f"{texto_reais} e {texto_centavos}"
        
        return texto_reais
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'tipo_recibo': self.tipo_recibo,
            'casa_id': self.casa_id,
            'inquilino_id': self.inquilino_id,
            'nome_pagador': self.nome_pagador,
            'cpf_pagador': self.cpf_pagador,
            'nome_recebedor': self.nome_recebedor,
            'cpf_recebedor': self.cpf_recebedor,
            'valor': self.valor,
            'descricao': self.descricao,
            'referente_a': self.referente_a,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'mes_referencia': self.mes_referencia,
            'ano_referencia': self.ano_referencia,
            'forma_pagamento': self.forma_pagamento,
            'observacoes': self.observacoes
        }