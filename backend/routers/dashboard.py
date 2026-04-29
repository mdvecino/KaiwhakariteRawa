from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, Any, List
from ..db import get_db
from ..auth.dependencies import get_current_user
from ..services.inventory_service import InventoryService
from ..models.users import User
from ..models.inventory import InventoryItem

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    inventory_service = InventoryService(db)
    stats = inventory_service.get_inventory_stats()
    
    return {
        **stats,  # Include all stats directly
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "full_name": current_user.full_name
        }
    }


@router.get("/low-stock-alerts")
async def get_low_stock_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get low stock alerts"""
    inventory_service = InventoryService(db)
    low_stock_items = inventory_service.get_low_stock_items()
    
    return {
        "alerts": [
            {
                "id": item.id,
                "name": item.name,
                "sku": item.sku,
                "current_quantity": item.quantity,
                "min_quantity": item.min_quantity,
                "category": item.category
            }
            for item in low_stock_items
        ],
        "count": len(low_stock_items)
    }


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activity (placeholder for future implementation)"""
    return {
        "activities": [
            {
                "id": 1,
                "type": "item_created",
                "description": "New item added to inventory",
                "timestamp": "2024-01-15T10:30:00Z",
                "user": "admin"
            },
            {
                "id": 2,
                "type": "low_stock_alert",
                "description": "Item quantity below minimum",
                "timestamp": "2024-01-15T09:15:00Z",
                "user": "system"
            }
        ]
    }


@router.get("/cultural-analytics")
async def get_cultural_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive Māori cultural analytics"""
    inventory_service = InventoryService(db)
    
    # Get all Māori items
    maori_items = inventory_service.get_maori_items()
    tapu_items = inventory_service.get_tapu_items()
    
    # Cultural categories analysis
    cultural_categories = ['taonga', 'raranga', 'whakairo', 'rongoa', 'kai', 'kakahu']
    category_stats = {}
    for category in cultural_categories:
        count = len([item for item in maori_items if item.category == category])
        category_stats[category] = count
    
    # Iwi distribution analysis
    iwi_distribution = {}
    for item in maori_items:
        if item.iwi:
            iwi_distribution[item.iwi] = iwi_distribution.get(item.iwi, 0) + 1
    
    # Tapu status analysis
    tapu_count = len(tapu_items)
    sacred_count = len([item for item in maori_items if item.is_sacred])
    
    # Age distribution analysis
    age_distribution = {
        'Hou': 0,  # Contemporary
        'Tawhito': 0,  # Recent
        'Taketake': 0,  # Traditional
        'Hītori': 0,  # Historic
        'Tawhito rawa': 0,  # Ancient
        'Unknown': 0
    }
    
    for item in maori_items:
        age = item.age_estimate or 'Unknown'
        if age in age_distribution:
            age_distribution[age] += 1
        else:
            age_distribution['Unknown'] += 1
    
    # Kaitiaki (guardians) analysis
    kaitiaki_items = len([item for item in maori_items if item.kaitiaki])
    
    # Cultural completeness score (percentage of items with cultural fields filled)
    cultural_fields = ['iwi', 'korero', 'whakapapa', 'tikanga_notes', 'cultural_significance', 'maori_name']
    completeness_scores = []
    
    for item in maori_items:
        filled_fields = 0
        for field in cultural_fields:
            if getattr(item, field, None):
                filled_fields += 1
        completeness_scores.append((filled_fields / len(cultural_fields)) * 100)
    
    avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
    
    # Items needing attention (low cultural completeness or missing kaitiaki for tapu items)
    items_needing_attention = []
    for item in maori_items:
        issues = []
        
        # Check cultural completeness
        filled_fields = sum(1 for field in cultural_fields if getattr(item, field, None))
        completeness = (filled_fields / len(cultural_fields)) * 100
        
        if completeness < 50:
            issues.append("Low cultural documentation")
        
        if item.tapu_status and not item.kaitiaki:
            issues.append("Tapu item missing kaitiaki")
        
        if item.is_sacred and item.loanable:
            issues.append("Sacred item marked as loanable")
        
        if issues:
            items_needing_attention.append({
                'id': item.id,
                'name': item.maori_name or item.name,
                'issues': issues,
                'completeness': round(completeness, 1)
            })
    
    return {
        'total_maori_items': len(maori_items),
        'cultural_categories': category_stats,
        'iwi_distribution': iwi_distribution,
        'tapu_status': {
            'tapu_items': tapu_count,
            'sacred_items': sacred_count,
            'regular_items': len(maori_items) - tapu_count
        },
        'age_distribution': age_distribution,
        'cultural_completeness': {
            'average_score': round(avg_completeness, 1),
            'items_with_kaitiaki': kaitiaki_items,
            'total_items': len(maori_items)
        },
        'items_needing_attention': items_needing_attention[:10],  # Top 10 items needing attention
        'cultural_health_score': round((avg_completeness + (kaitiaki_items / len(maori_items) * 100 if maori_items else 0)) / 2, 1)
    }


@router.get("/tapu-alerts")
async def get_tapu_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts for tapu (sacred) items requiring special attention"""
    inventory_service = InventoryService(db)
    tapu_items = inventory_service.get_tapu_items()
    
    alerts = []
    for item in tapu_items:
        alert_level = "info"
        messages = []
        
        # Check for missing kaitiaki
        if not item.kaitiaki:
            messages.append("No kaitiaki (guardian) assigned")
            alert_level = "warning"
        
        # Check if sacred item is marked as loanable
        if item.is_sacred and item.loanable:
            messages.append("Sacred item should not be loanable")
            alert_level = "error"
        
        # Check for missing cultural protocols
        if not item.tikanga_notes:
            messages.append("Missing tikanga (cultural protocols)")
            if alert_level == "info":
                alert_level = "warning"
        
        # Check for missing karakia
        if not item.karakia:
            messages.append("Consider adding karakia (prayers/blessings)")
        
        if messages:
            alerts.append({
                'id': item.id,
                'name': item.maori_name or item.name,
                'alert_level': alert_level,
                'messages': messages,
                'kaitiaki': item.kaitiaki,
                'iwi': item.iwi
            })
    
    return {
        'alerts': alerts,
        'total_tapu_items': len(tapu_items),
        'items_with_issues': len(alerts)
    } 