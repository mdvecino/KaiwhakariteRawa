from sqlalchemy import Column, Integer, String, Boolean
from ..models.base import BaseModel

class SystemSettings(BaseModel):
    __tablename__ = 'system_settings'
    # Only one row is expected; id=1
    system_name = Column(String(100), default='Kaiwhakarite Rawa')
    language = Column(String(20), default='English')
    timezone = Column(String(50), default='Pacific/Auckland')
    date_format = Column(String(20), default='DD/MM/YYYY')
    low_stock_threshold = Column(Integer, default=10)
    currency = Column(String(20), default='NZD - New Zealand Dollar')
    dark_mode = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=30)  # in minutes
    audit_log_enabled = Column(Boolean, default=True) 