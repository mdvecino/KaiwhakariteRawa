from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Enum, Date
)
from sqlalchemy.orm import relationship
import enum
from ..models.base import BaseModel


class EventType(str, enum.Enum):
    MATARIKI = "matariki"
    MARAMATAKA = "maramataka"
    CULTURAL = "cultural"
    MAINTENANCE = "maintenance"
    INVENTORY = "inventory"
    SEASONAL = "seasonal"
    HARVESTING = "harvesting"
    TAPU_PERIOD = "tapu_period"
    CEREMONY = "ceremony"
    WANANGA = "wananga"
    OTHER = "other"


class LunarPhase(str, enum.Enum):
    """Māori lunar phases for maramataka"""
    WHIRO = "whiro"  # New moon - not good for planting
    TIREA = "tirea"  # Day 2 - still not favorable
    HOAKA = "hoaka"  # Day 3 - crescent appears
    OHUA = "ohua"  # Day 4-6 - growing
    OKORO = "okoro"  # Day 7-9 - good for planting
    TAMATEA_A_TUTAHI = "tamatea_a_tutahi"  # Day 10-12 - very good
    TAMATEA_KAI_ARIKI = "tamatea_kai_ariki"  # Day 13-15 - excellent
    RAKAU_NUIS = "rakau_nuis"  # Day 16-17 - full moon period
    TAKIRAU = "takirau"  # Day 18-19 - good for harvesting
    ORONGONUI = "orongonui"  # Day 20-22 - favorable
    MAURI = "mauri"  # Day 23-25 - decreasing
    OMUTU = "omutu"  # Day 26-28 - not favorable
    MUTUWHENUA = "mutuwhenua"  # Day 29-30 - new moon approaching


class SeasonType(str, enum.Enum):
    """Māori seasons"""
    KOANGA = "koanga"  # Spring
    RAUMATI = "raumati"  # Summer
    NGAHURU = "ngahuru"  # Autumn
    HOTOKE = "hotoke"  # Winter


class CulturalGuideline(str, enum.Enum):
    """Cultural guidelines and restrictions"""
    TAPU = "tapu"  # Sacred/restricted
    NOA = "noa"  # Free/unrestricted
    RAHUI = "rahui"  # Temporary restriction
    RITENGA = "ritenga"  # Ceremony required
    KARAKIA = "karakia"  # Prayer/blessing needed


class CalendarEvent(BaseModel):
    """Enhanced calendar event model for Māori calendar integration"""
    __tablename__ = "calendar_events"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    
    # Timing
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    all_day = Column(Boolean, default=False)
    recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100), nullable=True)
    
    # Location and details
    location = Column(String(200), nullable=True)
    attendees = Column(Text, nullable=True)  # JSON array of user IDs
    notes = Column(Text, nullable=True)
    
    # Māori cultural fields
    iwi_connection = Column(String(100), nullable=True)
    cultural_significance = Column(Text, nullable=True)
    tikanga_requirements = Column(Text, nullable=True)
    cultural_guidelines = Column(Enum(CulturalGuideline), nullable=True)
    
    # Maramataka integration
    lunar_phase = Column(Enum(LunarPhase), nullable=True)
    season_type = Column(Enum(SeasonType), nullable=True)
    maramataka_notes = Column(Text, nullable=True)
    
    # Inventory integration
    related_items = Column(Text, nullable=True)  # JSON array of item IDs
    inventory_alerts = Column(Text, nullable=True)  # JSON array of alerts
    seasonal_tasks = Column(Text, nullable=True)  # JSON array of tasks
    
    # Status and visibility
    is_public = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    is_cultural_highlight = Column(Boolean, default=False)
    priority_level = Column(Integer, default=1)  # 1-5 scale
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = relationship("User", back_populates="calendar_events", cascade="all, delete")
    messages = relationship("Message", back_populates="related_event")


class MaramatakaDay(BaseModel):
    """Daily maramataka information"""
    __tablename__ = "maramataka_days"
    
    date = Column(Date, nullable=False, unique=True)
    lunar_phase = Column(Enum(LunarPhase), nullable=False)
    lunar_day = Column(Integer, nullable=False)  # 1-30
    season_type = Column(Enum(SeasonType), nullable=False)
    
    # Daily guidance
    favorable_activities = Column(Text, nullable=True)  # JSON array
    unfavorable_activities = Column(Text, nullable=True)  # JSON array
    cultural_guidelines = Column(Enum(CulturalGuideline), nullable=True)
    
    # Energy and recommendations
    energy_level = Column(Integer, default=3)  # 1-5 scale
    planting_favorable = Column(Boolean, default=False)
    harvesting_favorable = Column(Boolean, default=False)
    fishing_favorable = Column(Boolean, default=False)
    traveling_favorable = Column(Boolean, default=False)
    
    # Cultural notes
    traditional_name = Column(String(100), nullable=True)
    cultural_notes = Column(Text, nullable=True)
    tikanga_reminders = Column(Text, nullable=True)
    
    # Special designations
    is_special_day = Column(Boolean, default=False)
    special_significance = Column(Text, nullable=True)


class CulturalEvent(BaseModel):
    """Predefined cultural events and observances"""
    __tablename__ = "cultural_events"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    
    # Timing - can be fixed date or relative to lunar calendar
    month = Column(Integer, nullable=True)  # 1-12 for fixed dates
    day = Column(Integer, nullable=True)  # 1-31 for fixed dates
    lunar_phase_trigger = Column(Enum(LunarPhase), nullable=True)
    
    # Duration and recurrence
    duration_days = Column(Integer, default=1)
    is_annual = Column(Boolean, default=True)
    
    # Cultural significance
    iwi_specific = Column(String(200), nullable=True)  # Specific iwi
    region_specific = Column(String(200), nullable=True)  # Regional
    cultural_significance = Column(Text, nullable=True)
    traditional_practices = Column(Text, nullable=True)
    modern_observance = Column(Text, nullable=True)
    
    # Inventory connections
    related_inventory_categories = Column(Text, nullable=True)  # JSON array
    seasonal_inventory_tasks = Column(Text, nullable=True)  # JSON array
    
    # Status
    is_active = Column(Boolean, default=True)
    is_major_observance = Column(Boolean, default=False)


class InventoryAlert(BaseModel):
    """Calendar-based inventory alerts"""
    __tablename__ = "inventory_alerts"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(50), nullable=False)  # seasonal, cultural
    
    # Timing
    trigger_date = Column(Date, nullable=True)  # Fixed date
    lunar_phase_trigger = Column(Enum(LunarPhase), nullable=True)
    season_trigger = Column(Enum(SeasonType), nullable=True)
    days_before = Column(Integer, default=0)  # Days before trigger
    
    # Inventory connections
    inventory_item_ids = Column(Text, nullable=True)  # JSON array
    inventory_categories = Column(Text, nullable=True)  # JSON array
    
    # Alert details
    action_required = Column(Text, nullable=True)
    cultural_considerations = Column(Text, nullable=True)
    priority_level = Column(Integer, default=3)  # 1-5 scale
    
    # Status
    is_active = Column(Boolean, default=True)
    recurring = Column(Boolean, default=True)
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) 