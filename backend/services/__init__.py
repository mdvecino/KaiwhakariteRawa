# Services package 
from typing import Type, TypeVar, Generic, Optional, List
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseService(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, obj_id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in) -> T:
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, obj_id: int, obj_in) -> Optional[T]:
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return None
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, obj_id: int) -> bool:
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return False
        self.db.delete(db_obj)
        self.db.commit()
        return True 