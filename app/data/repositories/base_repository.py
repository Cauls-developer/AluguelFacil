from typing import Generic, TypeVar, Type, List, Optional

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Repositório base com operações CRUD genéricas"""
    
    def __init__(self, session, model: Type[T]):
        self.session = session
        self.model = model
    
    def create(self, entity: T) -> T:
        """Cria uma nova entidade"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Busca entidade por ID"""
        return self.session.query(self.model).filter(self.model.id == entity_id).first()
    
    def get_all(self) -> List[T]:
        """Retorna todas as entidades"""
        return self.session.query(self.model).all()
    
    def update(self, entity: T) -> T:
        """Atualiza uma entidade"""
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def delete(self, entity_id: int) -> bool:
        """Deleta uma entidade por ID"""
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

