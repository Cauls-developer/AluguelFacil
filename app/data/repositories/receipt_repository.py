from typing import List, Optional
from datetime import datetime, date
from app.data.models.receipt import Recibo
from app.data.repositories.base_repository import BaseRepository


class ReciboRepository(BaseRepository[Recibo]):
    """Repositório específico para Recibos"""
    
    def __init__(self, session):
        super().__init__(session, Recibo)
    
    def get_by_tipo(self, tipo_recibo: str) -> List[Recibo]:
        """Retorna recibos por tipo"""
        return self.session.query(Recibo).filter(
            Recibo.tipo_recibo == tipo_recibo
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_by_casa(self, casa_id: int) -> List[Recibo]:
        """Retorna todos os recibos de uma casa"""
        return self.session.query(Recibo).filter(
            Recibo.casa_id == casa_id
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_by_inquilino(self, inquilino_id: int) -> List[Recibo]:
        """Retorna todos os recibos de um inquilino"""
        return self.session.query(Recibo).filter(
            Recibo.inquilino_id == inquilino_id
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_by_periodo(self, mes: int, ano: int) -> List[Recibo]:
        """Retorna recibos por período de referência"""
        return self.session.query(Recibo).filter(
            Recibo.mes_referencia == mes,
            Recibo.ano_referencia == ano
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_by_data_pagamento(self, data_inicio: date, data_fim: date) -> List[Recibo]:
        """Retorna recibos por período de pagamento"""
        return self.session.query(Recibo).filter(
            Recibo.data_pagamento >= data_inicio,
            Recibo.data_pagamento <= data_fim
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_recibos_pagador(self, nome_pagador: str) -> List[Recibo]:
        """Busca recibos por nome do pagador (parcial)"""
        return self.session.query(Recibo).filter(
            Recibo.nome_pagador.ilike(f'%{nome_pagador}%')
        ).order_by(Recibo.data_pagamento.desc()).all()
    
    def get_total_recebido_periodo(self, data_inicio: date, data_fim: date) -> float:
        """Retorna o total recebido em um período"""
        recibos = self.get_by_data_pagamento(data_inicio, data_fim)
        return sum(r.valor for r in recibos)
    
    def get_total_por_tipo(self, tipo_recibo: str, data_inicio: date = None, data_fim: date = None) -> float:
        """Retorna o total recebido por tipo de recibo"""
        query = self.session.query(Recibo).filter(Recibo.tipo_recibo == tipo_recibo)
        
        if data_inicio:
            query = query.filter(Recibo.data_pagamento >= data_inicio)
        if data_fim:
            query = query.filter(Recibo.data_pagamento <= data_fim)
        
        recibos = query.all()
        return sum(r.valor for r in recibos)