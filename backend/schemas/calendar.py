from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from ..models.calendar import (
    EventType, LunarPhase, SeasonType, CulturalGuideline
)


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: EventType
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = False
    recurring: bool = False
    recurrence_pattern: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[str] = None
    notes: Optional[str] = None
    iwi_connection: Optional[str] = None
    cultural_significance: Optional[str] = None
    tikanga_requirements: Optional[str] = None
    cultural_guidelines: Optional[CulturalGuideline] = None
    lunar_phase: Optional[LunarPhase] = None
    season_type: Optional[SeasonType] = None
    maramataka_notes: Optional[str] = None
    related_items: Optional[str] = None
    inventory_alerts: Optional[str] = None
    seasonal_tasks: Optional[str] = None
    is_public: bool = True
    requires_approval: bool = False
    is_cultural_highlight: bool = False
    priority_level: int = 1


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    all_day: Optional[bool] = None
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[str] = None
    notes: Optional[str] = None
    iwi_connection: Optional[str] = None
    cultural_significance: Optional[str] = None
    tikanga_requirements: Optional[str] = None
    cultural_guidelines: Optional[CulturalGuideline] = None
    lunar_phase: Optional[LunarPhase] = None
    season_type: Optional[SeasonType] = None
    maramataka_notes: Optional[str] = None
    related_items: Optional[str] = None
    inventory_alerts: Optional[str] = None
    seasonal_tasks: Optional[str] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_cultural_highlight: Optional[bool] = None
    priority_level: Optional[int] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class CalendarEventList(BaseModel):
    events: List[CalendarEventResponse]
    total: int
    page: int
    per_page: int


# Maramataka Day Schemas
class MaramatakaDayBase(BaseModel):
    date: date
    lunar_phase: LunarPhase
    lunar_day: int
    season_type: SeasonType
    favorable_activities: Optional[str] = None
    unfavorable_activities: Optional[str] = None
    cultural_guidelines: Optional[CulturalGuideline] = None
    energy_level: int = 3
    planting_favorable: bool = False
    harvesting_favorable: bool = False
    fishing_favorable: bool = False
    traveling_favorable: bool = False
    traditional_name: Optional[str] = None
    cultural_notes: Optional[str] = None
    tikanga_reminders: Optional[str] = None
    is_special_day: bool = False
    special_significance: Optional[str] = None


class MaramatakaDayCreate(MaramatakaDayBase):
    pass


class MaramatakaDayUpdate(BaseModel):
    lunar_phase: Optional[LunarPhase] = None
    lunar_day: Optional[int] = None
    season_type: Optional[SeasonType] = None
    favorable_activities: Optional[str] = None
    unfavorable_activities: Optional[str] = None
    cultural_guidelines: Optional[CulturalGuideline] = None
    energy_level: Optional[int] = None
    planting_favorable: Optional[bool] = None
    harvesting_favorable: Optional[bool] = None
    fishing_favorable: Optional[bool] = None
    traveling_favorable: Optional[bool] = None
    traditional_name: Optional[str] = None
    cultural_notes: Optional[str] = None
    tikanga_reminders: Optional[str] = None
    is_special_day: Optional[bool] = None
    special_significance: Optional[str] = None


class MaramatakaDayResponse(MaramatakaDayBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Cultural Event Schemas
class CulturalEventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_type: EventType
    month: Optional[int] = None
    day: Optional[int] = None
    lunar_phase_trigger: Optional[LunarPhase] = None
    duration_days: int = 1
    is_annual: bool = True
    iwi_specific: Optional[str] = None
    region_specific: Optional[str] = None
    cultural_significance: Optional[str] = None
    traditional_practices: Optional[str] = None
    modern_observance: Optional[str] = None
    related_inventory_categories: Optional[str] = None
    seasonal_inventory_tasks: Optional[str] = None
    is_active: bool = True
    is_major_observance: bool = False


class CulturalEventCreate(CulturalEventBase):
    pass


class CulturalEventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    month: Optional[int] = None
    day: Optional[int] = None
    lunar_phase_trigger: Optional[LunarPhase] = None
    duration_days: Optional[int] = None
    is_annual: Optional[bool] = None
    iwi_specific: Optional[str] = None
    region_specific: Optional[str] = None
    cultural_significance: Optional[str] = None
    traditional_practices: Optional[str] = None
    modern_observance: Optional[str] = None
    related_inventory_categories: Optional[str] = None
    seasonal_inventory_tasks: Optional[str] = None
    is_active: Optional[bool] = None
    is_major_observance: Optional[bool] = None


class CulturalEventResponse(CulturalEventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Inventory Alert Schemas
class InventoryAlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    alert_type: str
    trigger_date: Optional[date] = None
    lunar_phase_trigger: Optional[LunarPhase] = None
    season_trigger: Optional[SeasonType] = None
    days_before: int = 0
    inventory_item_ids: Optional[str] = None
    inventory_categories: Optional[str] = None
    action_required: Optional[str] = None
    cultural_considerations: Optional[str] = None
    priority_level: int = 3
    is_active: bool = True
    recurring: bool = True


class InventoryAlertCreate(InventoryAlertBase):
    pass


class InventoryAlertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    alert_type: Optional[str] = None
    trigger_date: Optional[date] = None
    lunar_phase_trigger: Optional[LunarPhase] = None
    season_trigger: Optional[SeasonType] = None
    days_before: Optional[int] = None
    inventory_item_ids: Optional[str] = None
    inventory_categories: Optional[str] = None
    action_required: Optional[str] = None
    cultural_considerations: Optional[str] = None
    priority_level: Optional[int] = None
    is_active: Optional[bool] = None
    recurring: Optional[bool] = None


class InventoryAlertResponse(InventoryAlertBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Comprehensive Calendar Data Response
class CalendarDayData(BaseModel):
    """Complete calendar data for a specific day"""
    date: date
    maramataka_day: Optional[MaramatakaDayResponse] = None
    events: List[CalendarEventResponse] = []
    cultural_events: List[CulturalEventResponse] = []
    inventory_alerts: List[InventoryAlertResponse] = []
    lunar_phase: Optional[LunarPhase] = None
    season_type: Optional[SeasonType] = None
    is_special_day: bool = False
    cultural_guidelines: Optional[CulturalGuideline] = None


class CalendarMonthData(BaseModel):
    """Complete calendar data for a month"""
    year: int
    month: int
    days: List[CalendarDayData] = []
    
    
class TodayEventsResponse(BaseModel):
    """Today's events and alerts for dashboard"""
    today: date
    events: List[CalendarEventResponse] = []
    cultural_events: List[CulturalEventResponse] = []
    inventory_alerts: List[InventoryAlertResponse] = []
    maramataka_day: Optional[MaramatakaDayResponse] = None
    cultural_reminders: List[str] = []
    seasonal_tasks: List[str] = [] 