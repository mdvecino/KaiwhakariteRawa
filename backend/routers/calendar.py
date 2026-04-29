from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..db import get_db
from ..auth.dependencies import get_current_user, require_manager
from ..services.calendar_service import CalendarService
from ..schemas.calendar import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    MaramatakaDayCreate, MaramatakaDayResponse,
    CulturalEventCreate, CulturalEventResponse,
    InventoryAlertCreate, InventoryAlertResponse,
    CalendarDayData, CalendarMonthData, TodayEventsResponse
)
from ..models.users import User


router = APIRouter()

# Today's Events Route (must come before generic routes)
@router.get("/today", response_model=TodayEventsResponse)
async def get_today_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's events and alerts for dashboard"""
    calendar_service = CalendarService(db)
    return calendar_service.get_today_events()


# Setup Route (must come before generic routes)
@router.post("/setup/cultural-events")
async def initialize_cultural_events(
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Initialize default cultural events (admin only)"""
    calendar_service = CalendarService(db)
    calendar_service.initialize_cultural_events()
    return {"message": "Cultural events initialized successfully"}


# Maramataka Routes
@router.post("/maramataka", response_model=MaramatakaDayResponse)
async def create_maramataka_day(
    maramataka_data: MaramatakaDayCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create maramataka day information"""
    calendar_service = CalendarService(db)
    return calendar_service.create_maramataka_day(maramataka_data)


@router.get("/maramataka/{target_date}", response_model=MaramatakaDayResponse)
async def get_maramataka_day(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get maramataka information for a specific date"""
    calendar_service = CalendarService(db)
    maramataka_day = calendar_service.get_maramataka_day(target_date)
    if not maramataka_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maramataka information not found for this date"
        )
    return maramataka_day


@router.get("/maramataka/{year}/{month}", response_model=List[MaramatakaDayResponse])
async def get_maramataka_month(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get maramataka information for entire month"""
    calendar_service = CalendarService(db)
    return calendar_service.get_maramataka_month(year, month)


# Cultural Event Routes
@router.post("/cultural", response_model=CulturalEventResponse)
async def create_cultural_event(
    event_data: CulturalEventCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new cultural event template"""
    calendar_service = CalendarService(db)
    return calendar_service.create_cultural_event(event_data)


@router.get("/cultural", response_model=List[CulturalEventResponse])
async def get_cultural_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all cultural events"""
    calendar_service = CalendarService(db)
    return calendar_service.get_cultural_events()


@router.get("/cultural/{target_date}", response_model=List[CulturalEventResponse])
async def get_cultural_events_for_date(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cultural events for specific date"""
    calendar_service = CalendarService(db)
    return calendar_service.get_cultural_events_for_date(target_date)


# Inventory Alert Routes
@router.post("/alerts", response_model=InventoryAlertResponse)
async def create_inventory_alert(
    alert_data: InventoryAlertCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create inventory alert"""
    calendar_service = CalendarService(db)
    return calendar_service.create_inventory_alert(alert_data, current_user.id)


@router.get("/alerts/{target_date}", response_model=List[InventoryAlertResponse])
async def get_inventory_alerts_for_date(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inventory alerts for specific date"""
    calendar_service = CalendarService(db)
    return calendar_service.get_inventory_alerts_for_date(target_date)


# Comprehensive Calendar Routes
@router.get("/day/{target_date}", response_model=CalendarDayData)
async def get_calendar_day_data(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete calendar data for a specific day"""
    calendar_service = CalendarService(db)
    return calendar_service.get_calendar_day_data(target_date)


@router.get("/month/{year}/{month}", response_model=CalendarMonthData)
async def get_calendar_month_data(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete calendar data for a month"""
    calendar_service = CalendarService(db)
    return calendar_service.get_calendar_month_data(year, month)


# Generic Calendar Event Routes (must come after specific routes)
@router.post("/", response_model=CalendarEventResponse)
async def create_event(
    event_data: CalendarEventCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new calendar event"""
    calendar_service = CalendarService(db)
    event = calendar_service.create_event(event_data, current_user.id)
    return event


@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all calendar events"""
    calendar_service = CalendarService(db)
    return calendar_service.get_events(skip=skip, limit=limit)


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar event by ID"""
    calendar_service = CalendarService(db)
    event = calendar_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update calendar event"""
    calendar_service = CalendarService(db)
    event = calendar_service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Delete calendar event"""
    calendar_service = CalendarService(db)
    success = calendar_service.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return {"message": "Event deleted successfully"} 