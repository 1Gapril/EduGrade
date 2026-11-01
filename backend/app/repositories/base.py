"""Base Repository com operações CRUD genéricas."""

from typing import Generic, TypeVar, Optional, List, Any
from uuid import UUID

from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import Session, Query

from backend.app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository base com operações CRUD comuns."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[ModelType]:
        """Busca por ID."""
        return self.db.get(self.model, id)

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Busca por campo específico."""
        stmt = select(self.model).where(getattr(self.model, field) == value)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[ModelType]:
        """Lista todos com paginação e filtros."""
        stmt = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            stmt = stmt.order_by(column.desc() if order_desc else column)

        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, filters: Optional[dict] = None) -> int:
        """Conta total com filtros."""
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)

        return self.db.execute(stmt).scalar_one()

    def create(self, obj_in: dict) -> ModelType:
        """Cria novo registro."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.flush()
        return db_obj

    def update(self, id: UUID, obj_in: dict) -> Optional[ModelType]:
        """Atualiza registro."""
        db_obj = self.get(id)
        if not db_obj:
            return None

        for key, value in obj_in.items():
            if hasattr(db_obj, key) and value is not None:
                setattr(db_obj, key, value)

        self.db.flush()
        return db_obj

    def delete(self, id: UUID) -> bool:
        """Deleta registro."""
        db_obj = self.get(id)
        if not db_obj:
            return False

        self.db.delete(db_obj)
        self.db.flush()
        return True

    def exists(self, id: UUID) -> bool:
        """Verifica se existe."""
        return self.get(id) is not None

    def bulk_create(self, objects: List[dict]) -> List[ModelType]:
        """Cria em lote."""
        db_objects = [self.model(**obj) for obj in objects]
        self.db.add_all(db_objects)
        self.db.flush()
        return db_objects

    def bulk_update(self, updates: List[dict]) -> int:
        """Atualiza em lote. Cada dict deve conter 'id'."""
        count = 0
        for update_data in updates:
            id = update_data.pop("id", None)
            if id and self.update(id, update_data):
                count += 1
        return count