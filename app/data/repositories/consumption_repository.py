from typing import List, Optional
from app.data.models.consumption import Consumo
from app.data.repositories.base_repository import BaseRepository


class ConsumoRepository(BaseRepository[Consumo]):
    """Repositório específico para Consumos"""
    
    def __init__(self, session):
        super().__init__(session, Consumo)
    
    def get_by_casa_e_periodo(self, casa_id: int, mes: int, ano: int) -> Optional[Consumo]:
        """Busca consumo por casa e período"""
        return self.session.query(Consumo).filter(
            Consumo.casa_id == casa_id,
            Consumo.mes == mes,
            Consumo.ano == ano
        ).first()
    
    def get_consumos_por_casa(self, casa_id: int) -> List[Consumo]:
        """Retorna todos os consumos de uma casa ordenados por data"""
        return self.session.query(Consumo).filter(
            Consumo.casa_id == casa_id
        ).order_by(Consumo.ano.desc(), Consumo.mes.desc()).all()
    
    def get_ultimo_consumo(self, casa_id: int) -> Optional[Consumo]:
        """Retorna o último consumo registrado de uma casa"""
        return self.session.query(Consumo).filter(
            Consumo.casa_id == casa_id
        ).order_by(Consumo.ano.desc(), Consumo.mes.desc()).first()
