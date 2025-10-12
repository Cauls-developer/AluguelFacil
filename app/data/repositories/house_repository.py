from typing import List, Optional
from app.data.models.house import Casa
from app.data.repositories.base_repository import BaseRepository


class CasaRepository(BaseRepository[Casa]):
    """Repositório específico para Casas"""
    
    def __init__(self, session):
        super().__init__(session, Casa)
    
    def get_by_inquilino(self, inquilino_id: int) -> Optional[Casa]:
        """Busca casa por inquilino"""
        return self.session.query(Casa).filter(Casa.inquilino_id == inquilino_id).first()
    
    def get_casas_disponiveis(self) -> List[Casa]:
        """Retorna casas sem inquilino"""
        return self.session.query(Casa).filter(Casa.inquilino_id.is_(None)).all()

