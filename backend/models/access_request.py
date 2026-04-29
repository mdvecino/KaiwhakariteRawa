from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..models.base import Base
from ..models.users import User
import enum
from ..models.base import BaseModel

class AccessRequestStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class AccessRequest(Base):
    __tablename__ = 'access_requests'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    username = Column(String, nullable=False)
    requested_role = Column(String, nullable=True)
    requested_page = Column(String, nullable=True)
    message = Column(String, nullable=True)
    status = Column(Enum(AccessRequestStatus), default=AccessRequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', backref='access_requests') 