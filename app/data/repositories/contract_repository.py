from typing import List, Optional
from datetime import datetime, date
from app.data.models.contract import Contrato
from app.data.repositories.base_repository import BaseRepository


class ContratoRepository(BaseRepository[Contrato]):
    """Repositório específico para Contratos"""
    
    def __init__(self, session):
        super().__init__(session, Contrato)
    
    def get_contratos_ativos(self) -> List[Contrato]:
        """Retorna todos os contratos ativos"""
        return self.session.query(Contrato).filter(Contrato.ativo == 1).all()
    
    def get_contratos_vigentes(self) -> List[Contrato]:
        """Retorna contratos vigentes (ativos e dentro do período)"""
        hoje = date.today()
        return self.session.query(Contrato).filter(
            Contrato.ativo == 1,
            Contrato.data_inicio <= hoje,
            Contrato.data_fim >= hoje
        ).all()
    
    def get_contratos_vencidos(self) -> List[Contrato]:
        """Retorna contratos vencidos mas ainda ativos"""
        hoje = date.today()
        return self.session.query(Contrato).filter(
            Contrato.ativo == 1,
            Contrato.data_fim < hoje
        ).all()
    
    def get_by_casa(self, casa_id: int) -> List[Contrato]:
        """Retorna todos os contratos de uma casa"""
        return self.session.query(Contrato).filter(
            Contrato.casa_id == casa_id
        ).order_by(Contrato.data_inicio.desc()).all()
    
    def get_by_inquilino(self, inquilino_id: int) -> List[Contrato]:
        """Retorna todos os contratos de um inquilino"""
        return self.session.query(Contrato).filter(
            Contrato.inquilino_id == inquilino_id
        ).order_by(Contrato.data_inicio.desc()).all()
    
    def get_contrato_ativo_casa(self, casa_id: int) -> Optional[Contrato]:
        """Retorna o contrato ativo de uma casa específica"""
        return self.session.query(Contrato).filter(
            Contrato.casa_id == casa_id,
            Contrato.ativo == 1
        ).first()
    
    def get_contrato_vigente_casa(self, casa_id: int) -> Optional[Contrato]:
        """Retorna o contrato vigente de uma casa (ativo e no período)"""
        hoje = date.today()
        return self.session.query(Contrato).filter(
            Contrato.casa_id == casa_id,
            Contrato.ativo == 1,
            Contrato.data_inicio <= hoje,
            Contrato.data_fim >= hoje
        ).first()
    
    def encerrar_contrato(self, contrato_id: int) -> bool:
        """Encerra um contrato (marca como inativo)"""
        contrato = self.get_by_id(contrato_id)
        if contrato:
            contrato.ativo = 0
            self.session.commit()
            return True
        return False
    
    def reativar_contrato(self, contrato_id: int) -> bool:
        """Reativa um contrato"""
        contrato = self.get_by_id(contrato_id)
        if contrato:
            contrato.ativo = 1
            self.session.commit()
            return True
        return False