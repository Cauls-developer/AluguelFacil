from typing import List, Optional
from app.data.models.Tenant import Inquilino
from app.data.repositories.base_repository import BaseRepository


class InquilinoRepository(BaseRepository[Inquilino]):
    """Repositório específico para Inquilinos"""
    
    def __init__(self, session):
        super().__init__(session, Inquilino)
    
    def get_by_cpf(self, cpf: str) -> Optional[Inquilino]:
        """Busca inquilino por CPF"""
        return self.session.query(Inquilino).filter(Inquilino.cpf == cpf).first()
    
    def search_by_name(self, nome: str) -> List[Inquilino]:
        """Busca inquilinos por nome (parcial)"""
        return self.session.query(Inquilino).filter(
            Inquilino.nome_completo.ilike(f'%{nome}%')
        ).all()
