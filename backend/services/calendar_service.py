from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, timedelta
import json
import calendar

from ..models.calendar import (
    CalendarEvent, MaramatakaDay, CulturalEvent, InventoryAlert,
    EventType, LunarPhase, SeasonType, CulturalGuideline
)
from ..schemas.calendar import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    MaramatakaDayCreate, MaramatakaDayResponse,
    CulturalEventCreate, CulturalEventResponse,
    InventoryAlertCreate, InventoryAlertResponse,
    CalendarDayData, CalendarMonthData, TodayEventsResponse
)


class CalendarService:
    """Service class for calendar event management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Calendar Event Methods
    def create_event(self, event_data: CalendarEventCreate, user_id: int) -> CalendarEventResponse:
        """Create a new calendar event"""
        db_event = CalendarEvent(
            **event_data.dict(),
            created_by_id=user_id
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return CalendarEventResponse.from_orm(db_event)
    
    def get_event_by_id(self, event_id: int) -> Optional[CalendarEventResponse]:
        """Get calendar event by ID"""
        event = self.db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.is_active == True
        ).first()
        return CalendarEventResponse.from_orm(event) if event else None
    
    def get_events(self, skip: int = 0, limit: int = 100) -> List[CalendarEventResponse]:
        """Get all calendar events"""
        events = self.db.query(CalendarEvent).filter(
            CalendarEvent.is_active == True
        ).offset(skip).limit(limit).all()
        return [CalendarEventResponse.from_orm(event) for event in events]
    
    def update_event(self, event_id: int, event_data: CalendarEventUpdate) -> Optional[CalendarEventResponse]:
        """Update calendar event"""
        event = self.db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.is_active == True
        ).first()
        
        if not event:
            return None
        
        update_data = event_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        self.db.commit()
        self.db.refresh(event)
        return CalendarEventResponse.from_orm(event)
    
    def delete_event(self, event_id: int) -> bool:
        """Delete calendar event (soft delete)"""
        event = self.db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.is_active == True
        ).first()
        
        if not event:
            return False
        
        event.is_active = False
        self.db.commit()
        return True

    # Maramataka Day Methods
    def create_maramataka_day(self, maramataka_data: MaramatakaDayCreate) -> MaramatakaDayResponse:
        """Create maramataka day information"""
        db_day = MaramatakaDay(**maramataka_data.dict())
        self.db.add(db_day)
        self.db.commit()
        self.db.refresh(db_day)
        return MaramatakaDayResponse.from_orm(db_day)

    def get_maramataka_day(self, target_date: date) -> Optional[MaramatakaDayResponse]:
        """Get maramataka information for a specific date"""
        maramataka_day = self.db.query(MaramatakaDay).filter(
            MaramatakaDay.date == target_date,
            MaramatakaDay.is_active == True
        ).first()
        
        if not maramataka_day:
            # Generate maramataka day if not exists
            maramataka_day = self._generate_maramataka_day(target_date)
        
        return MaramatakaDayResponse.from_orm(maramataka_day) if maramataka_day else None

    def get_maramataka_month(self, year: int, month: int) -> List[MaramatakaDayResponse]:
        """Get maramataka information for entire month"""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        maramataka_days = self.db.query(MaramatakaDay).filter(
            MaramatakaDay.date >= start_date,
            MaramatakaDay.date <= end_date,
            MaramatakaDay.is_active == True
        ).all()
        
        # Generate missing days
        existing_dates = {day.date for day in maramataka_days}
        all_dates = {start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)}
        missing_dates = all_dates - existing_dates
        
        for missing_date in missing_dates:
            new_day = self._generate_maramataka_day(missing_date)
            if new_day:
                maramataka_days.append(new_day)
        
        return [MaramatakaDayResponse.from_orm(day) for day in sorted(maramataka_days, key=lambda x: x.date)]

    def _generate_maramataka_day(self, target_date: date) -> Optional[MaramatakaDay]:
        """Generate maramataka day based on lunar calculations"""
        # Simple lunar phase calculation (in real implementation, use proper lunar calendar)
        # This is a basic approximation for demonstration
        base_new_moon = date(2024, 1, 11)  # Known new moon date
        days_since_base = (target_date - base_new_moon).days
        lunar_day = (days_since_base % 30) + 1
        
        # Map lunar day to phase
        phase_mapping = {
            1: LunarPhase.WHIRO,
            2: LunarPhase.TIREA,
            3: LunarPhase.HOAKA,
            4: LunarPhase.OHUA, 5: LunarPhase.OHUA, 6: LunarPhase.OHUA,
            7: LunarPhase.OKORO, 8: LunarPhase.OKORO, 9: LunarPhase.OKORO,
            10: LunarPhase.TAMATEA_A_TUTAHI, 11: LunarPhase.TAMATEA_A_TUTAHI, 12: LunarPhase.TAMATEA_A_TUTAHI,
            13: LunarPhase.TAMATEA_KAI_ARIKI, 14: LunarPhase.TAMATEA_KAI_ARIKI, 15: LunarPhase.TAMATEA_KAI_ARIKI,
            16: LunarPhase.RAKAU_NUIS, 17: LunarPhase.RAKAU_NUIS,
            18: LunarPhase.TAKIRAU, 19: LunarPhase.TAKIRAU,
            20: LunarPhase.ORONGONUI, 21: LunarPhase.ORONGONUI, 22: LunarPhase.ORONGONUI,
            23: LunarPhase.MAURI, 24: LunarPhase.MAURI, 25: LunarPhase.MAURI,
            26: LunarPhase.OMUTU, 27: LunarPhase.OMUTU, 28: LunarPhase.OMUTU,
            29: LunarPhase.MUTUWHENUA, 30: LunarPhase.MUTUWHENUA
        }
        
        lunar_phase = phase_mapping.get(lunar_day, LunarPhase.WHIRO)
        season = self._get_season_for_date(target_date)
        
        # Generate cultural guidance based on lunar phase
        favorable_activities, unfavorable_activities = self._get_activities_for_phase(lunar_phase)
        energy_level = self._get_energy_level_for_phase(lunar_phase)
        
        db_day = MaramatakaDay(
            date=target_date,
            lunar_phase=lunar_phase,
            lunar_day=lunar_day,
            season_type=season,
            favorable_activities=json.dumps(favorable_activities),
            unfavorable_activities=json.dumps(unfavorable_activities),
            energy_level=energy_level,
            planting_favorable=lunar_phase in [LunarPhase.OKORO, LunarPhase.TAMATEA_A_TUTAHI, LunarPhase.TAMATEA_KAI_ARIKI],
            harvesting_favorable=lunar_phase in [LunarPhase.TAKIRAU, LunarPhase.ORONGONUI],
            fishing_favorable=lunar_phase in [LunarPhase.RAKAU_NUIS, LunarPhase.TAKIRAU],
            traveling_favorable=lunar_phase not in [LunarPhase.WHIRO, LunarPhase.TIREA, LunarPhase.OMUTU],
            traditional_name=lunar_phase.value.replace('_', ' ').title(),
            cultural_notes=self._get_cultural_notes_for_phase(lunar_phase),
            cultural_guidelines=self._get_cultural_guidelines_for_phase(lunar_phase)
        )
        
        self.db.add(db_day)
        self.db.commit()
        self.db.refresh(db_day)
        return db_day

    def _get_season_for_date(self, target_date: date) -> SeasonType:
        """Determine Māori season for date (Southern Hemisphere)"""
        month = target_date.month
        if month in [9, 10, 11]:  # Sep, Oct, Nov
            return SeasonType.KOANGA  # Spring
        elif month in [12, 1, 2]:  # Dec, Jan, Feb
            return SeasonType.RAUMATI  # Summer
        elif month in [3, 4, 5]:  # Mar, Apr, May
            return SeasonType.NGAHURU  # Autumn
        else:  # Jun, Jul, Aug
            return SeasonType.HOTOKE  # Winter

    def _get_activities_for_phase(self, lunar_phase: LunarPhase) -> tuple:
        """Get favorable and unfavorable activities for lunar phase"""
        activities_map = {
            LunarPhase.WHIRO: (["rest", "reflection"], ["planting", "new projects"]),
            LunarPhase.TIREA: (["planning", "preparation"], ["harvesting", "fishing"]),
            LunarPhase.HOAKA: (["small beginnings", "cleansing"], ["major decisions"]),
            LunarPhase.OHUA: (["growth activities", "learning"], ["clearing land"]),
            LunarPhase.OKORO: (["planting", "building"], ["destroying", "cutting"]),
            LunarPhase.TAMATEA_A_TUTAHI: (["planting", "construction", "ceremonies"], ["conflict"]),
            LunarPhase.TAMATEA_KAI_ARIKI: (["important ceremonies", "planting", "building"], ["arguments"]),
            LunarPhase.RAKAU_NUIS: (["fishing", "gathering", "celebrations"], ["planting"]),
            LunarPhase.TAKIRAU: (["harvesting", "fishing", "gathering"], ["planting seeds"]),
            LunarPhase.ORONGONUI: (["harvesting", "preserving", "storing"], ["new plantings"]),
            LunarPhase.MAURI: (["maintenance", "repairs"], ["starting new projects"]),
            LunarPhase.OMUTU: (["rest", "indoor activities"], ["outdoor work", "travel"]),
            LunarPhase.MUTUWHENUA: (["planning", "preparation"], ["planting", "harvesting"])
        }
        return activities_map.get(lunar_phase, ([], []))

    def _get_energy_level_for_phase(self, lunar_phase: LunarPhase) -> int:
        """Get energy level (1-5) for lunar phase"""
        energy_map = {
            LunarPhase.WHIRO: 1,
            LunarPhase.TIREA: 2,
            LunarPhase.HOAKA: 2,
            LunarPhase.OHUA: 3,
            LunarPhase.OKORO: 4,
            LunarPhase.TAMATEA_A_TUTAHI: 5,
            LunarPhase.TAMATEA_KAI_ARIKI: 5,
            LunarPhase.RAKAU_NUIS: 5,
            LunarPhase.TAKIRAU: 4,
            LunarPhase.ORONGONUI: 4,
            LunarPhase.MAURI: 3,
            LunarPhase.OMUTU: 2,
            LunarPhase.MUTUWHENUA: 2
        }
        return energy_map.get(lunar_phase, 3)

    def _get_cultural_notes_for_phase(self, lunar_phase: LunarPhase) -> str:
        """Get cultural notes for lunar phase"""
        notes_map = {
            LunarPhase.WHIRO: "Time of darkness and rest. Avoid important activities.",
            LunarPhase.TIREA: "Time for quiet reflection and planning ahead.",
            LunarPhase.HOAKA: "The crescent moon appears. Time for gentle beginnings.",
            LunarPhase.OHUA: "Growth phase begins. Good time for nurturing activities.",
            LunarPhase.OKORO: "Strong energy for planting and building projects.",
            LunarPhase.TAMATEA_A_TUTAHI: "Excellent time for all positive activities.",
            LunarPhase.TAMATEA_KAI_ARIKI: "Peak energy. Best time for ceremonies and planting.",
            LunarPhase.RAKAU_NUIS: "Full moon energy. Good for fishing and gathering.",
            LunarPhase.TAKIRAU: "Harvest time. Gather what has been planted.",
            LunarPhase.ORONGONUI: "Continue harvesting and preserving food.",
            LunarPhase.MAURI: "Energy waning. Time for maintenance and repairs.",
            LunarPhase.OMUTU: "Low energy period. Stay close to home.",
            LunarPhase.MUTUWHENUA: "Preparing for new cycle. Plan and prepare."
        }
        return notes_map.get(lunar_phase, "")

    def _get_cultural_guidelines_for_phase(self, lunar_phase: LunarPhase) -> CulturalGuideline:
        """Get cultural guidelines for lunar phase"""
        if lunar_phase in [LunarPhase.WHIRO, LunarPhase.TIREA, LunarPhase.OMUTU]:
            return CulturalGuideline.TAPU  # Restricted activities
        elif lunar_phase in [LunarPhase.TAMATEA_A_TUTAHI, LunarPhase.TAMATEA_KAI_ARIKI]:
            return CulturalGuideline.KARAKIA  # Blessing recommended
        else:
            return CulturalGuideline.NOA  # Free activities

    # Cultural Event Methods
    def create_cultural_event(self, event_data: CulturalEventCreate) -> CulturalEventResponse:
        """Create a new cultural event template"""
        db_event = CulturalEvent(**event_data.dict())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return CulturalEventResponse.from_orm(db_event)

    def get_cultural_events(self) -> List[CulturalEventResponse]:
        """Get all active cultural events"""
        events = self.db.query(CulturalEvent).filter(
            CulturalEvent.is_active == True
        ).all()
        return [CulturalEventResponse.from_orm(event) for event in events]

    def get_cultural_events_for_date(self, target_date: date) -> List[CulturalEventResponse]:
        """Get cultural events for specific date, including multi-day events"""
        # Fetch all active events for the month
        events = self.db.query(CulturalEvent).filter(
            CulturalEvent.is_active == True,
            CulturalEvent.month == target_date.month
        ).all()

        matching_events = []
        for event in events:
            if event.day is not None and event.duration_days is not None:
                try:
                    start = date(target_date.year, event.month, event.day)
                    end = start + timedelta(days=event.duration_days - 1)
                    if start <= target_date <= end:
                        matching_events.append(event)
                except Exception:
                    continue
            elif event.day == target_date.day:
                matching_events.append(event)
            # Lunar phase events
            elif event.lunar_phase_trigger is not None:
                maramataka_day = self.get_maramataka_day(target_date)
                if maramataka_day and event.lunar_phase_trigger == maramataka_day.lunar_phase:
                    matching_events.append(event)
        return [CulturalEventResponse.from_orm(event) for event in matching_events]

    # Inventory Alert Methods
    def create_inventory_alert(self, alert_data: InventoryAlertCreate, user_id: int) -> InventoryAlertResponse:
        """Create inventory alert"""
        db_alert = InventoryAlert(
            **alert_data.dict(),
            created_by_id=user_id
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)
        return InventoryAlertResponse.from_orm(db_alert)

    def get_inventory_alerts_for_date(self, target_date: date) -> List[InventoryAlertResponse]:
        """Get inventory alerts for specific date"""
        alerts = self.db.query(InventoryAlert).filter(
            InventoryAlert.is_active == True,
            or_(
                InventoryAlert.trigger_date == target_date,
                InventoryAlert.lunar_phase_trigger.isnot(None),
                InventoryAlert.season_trigger.isnot(None)
            )
        ).all()
        
        # Filter phase and season alerts
        maramataka_day = self.get_maramataka_day(target_date)
        if maramataka_day:
            phase_alerts = [a for a in alerts if a.lunar_phase_trigger == maramataka_day.lunar_phase]
            season_alerts = [a for a in alerts if a.season_trigger == maramataka_day.season_type]
            fixed_alerts = [a for a in alerts if a.trigger_date == target_date]
            alerts = phase_alerts + season_alerts + fixed_alerts
        
        return [InventoryAlertResponse.from_orm(alert) for alert in alerts]

    # Comprehensive Calendar Methods
    def get_calendar_day_data(self, target_date: date) -> CalendarDayData:
        """Get complete calendar data for a specific day"""
        # Get all data for the day
        events = self.db.query(CalendarEvent).filter(
            CalendarEvent.is_active == True,
            func.date(CalendarEvent.start_date) == target_date
        ).all()
        
        maramataka_day = self.get_maramataka_day(target_date)
        cultural_events = self.get_cultural_events_for_date(target_date)
        inventory_alerts = self.get_inventory_alerts_for_date(target_date)
        
        return CalendarDayData(
            date=target_date,
            maramataka_day=maramataka_day,
            events=[CalendarEventResponse.from_orm(e) for e in events],
            cultural_events=cultural_events,
            inventory_alerts=inventory_alerts,
            lunar_phase=maramataka_day.lunar_phase if maramataka_day else None,
            season_type=maramataka_day.season_type if maramataka_day else None,
            is_special_day=maramataka_day.is_special_day if maramataka_day else False,
            cultural_guidelines=maramataka_day.cultural_guidelines if maramataka_day else None
        )

    def get_calendar_month_data(self, year: int, month: int) -> CalendarMonthData:
        """Get complete calendar data for a month"""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        
        # Get all days data
        days_data = []
        current_date = start_date
        while current_date <= end_date:
            day_data = self.get_calendar_day_data(current_date)
            days_data.append(day_data)
            current_date += timedelta(days=1)
        
        return CalendarMonthData(
            year=year,
            month=month,
            days=days_data
        )

    def get_today_events(self) -> TodayEventsResponse:
        """Get today's events and alerts for dashboard"""
        today = date.today()
        day_data = self.get_calendar_day_data(today)
        
        # Generate cultural reminders
        cultural_reminders = []
        if day_data.maramataka_day:
            cultural_reminders.append(f"Today is {day_data.maramataka_day.traditional_name}")
            if day_data.maramataka_day.cultural_notes:
                cultural_reminders.append(day_data.maramataka_day.cultural_notes)
        
        # Generate seasonal tasks
        seasonal_tasks = []
        if day_data.maramataka_day:
            if day_data.maramataka_day.planting_favorable:
                seasonal_tasks.append("Good day for planting")
            if day_data.maramataka_day.harvesting_favorable:
                seasonal_tasks.append("Favorable for harvesting")
            if day_data.maramataka_day.fishing_favorable:
                seasonal_tasks.append("Good fishing conditions")
        
        return TodayEventsResponse(
            today=today,
            events=day_data.events,
            cultural_events=day_data.cultural_events,
            inventory_alerts=day_data.inventory_alerts,
            maramataka_day=day_data.maramataka_day,
            cultural_reminders=cultural_reminders,
            seasonal_tasks=seasonal_tasks
        )

    # Setup Methods
    def initialize_cultural_events(self):
        """Initialize default cultural events"""
        default_events = [
            {
                "name": "Matariki",
                "description": "Māori New Year celebration",
                "event_type": EventType.MATARIKI,
                "month": 6,
                "day": 21,
                "duration_days": 7,
                "cultural_significance": "Rising of the Matariki star cluster marks the Māori New Year",
                "traditional_practices": "Honoring ancestors, sharing food, planning for the year ahead",
                "modern_observance": "Family gatherings, cultural performances, reflection",
                "is_major_observance": True
            },
            {
                "name": "New Moon Ceremony",
                "description": "Monthly new moon observance",
                "event_type": EventType.CEREMONY,
                "lunar_phase_trigger": LunarPhase.WHIRO,
                "cultural_significance": "Time for reflection and setting intentions",
                "traditional_practices": "Quiet contemplation, karakia, planning",
                "modern_observance": "Meditation, goal setting, cultural reflection",
                "is_major_observance": False
            },
            {
                "name": "Full Moon Gathering",
                "description": "Monthly full moon activities",
                "event_type": EventType.CEREMONY,
                "lunar_phase_trigger": LunarPhase.RAKAU_NUIS,
                "cultural_significance": "Time of peak energy and community gathering",
                "traditional_practices": "Fishing, gathering, celebrations",
                "modern_observance": "Community events, cultural sharing, celebrations",
                "is_major_observance": False
            }
        ]
        
        for event_data in default_events:
            existing = self.db.query(CulturalEvent).filter(
                CulturalEvent.name == event_data["name"]
            ).first()
            
            if not existing:
                db_event = CulturalEvent(**event_data)
                self.db.add(db_event)
        
        self.db.commit() 