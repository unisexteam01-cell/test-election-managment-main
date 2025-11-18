from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timedelta
import logging

from auth import get_current_user, require_role
from database import get_database

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

@router.get("/karyakarta")
async def get_karyakarta_dashboard(
    current_user: dict = Depends(require_role(["karyakarta"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get karyakarta dashboard data"""
    query = {"assigned_to": current_user["sub"]}
    
    # Voter stats
    total_assigned = await db.voters.count_documents(query)
    visited = await db.voters.count_documents({**query, "visited_status": True})
    voted = await db.voters.count_documents({**query, "voted_status": True})
    
    # Survey stats
    total_surveys = await db.surveys.count_documents({"karyakarta_id": current_user["sub"]})
    
    # Tasks
    pending_tasks = await db.tasks.count_documents({
        "assigned_to": current_user["sub"],
        "status": "pending"
    })
    
    # Today's activity
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_surveys = await db.surveys.count_documents({
        "karyakarta_id": current_user["sub"],
        "timestamp": {"$gte": today_start}
    })
    
    today_visits = await db.voters.count_documents({
        "visited_by": current_user["sub"],
        "visited_date": {"$gte": today_start}
    })
    
    return {
        "assigned_voters": total_assigned,
        "visited_voters": visited,
        "voted_voters": voted,
        "coverage_percentage": (visited / total_assigned * 100) if total_assigned > 0 else 0,
        "total_surveys": total_surveys,
        "pending_tasks": pending_tasks,
        "today_surveys": today_surveys,
        "today_visits": today_visits
    }

@router.get("/admin")
async def get_admin_dashboard(
    current_user: dict = Depends(require_role(["admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get admin dashboard data"""
    # Get all karyakartas under this admin
    karyakartas = await db.users.find({
        "assigned_admin_id": current_user["sub"],
        "role": "karyakarta"
    }).to_list(1000)
    
    karyakarta_ids = [str(k["_id"]) for k in karyakartas]
    
    # Voter stats
    total_voters = await db.voters.count_documents({})
    assigned_voters = await db.voters.count_documents({"assigned_to": {"$in": karyakarta_ids}})
    visited = await db.voters.count_documents({"visited_status": True})
    voted = await db.voters.count_documents({"voted_status": True})
    
    # Survey stats
    total_surveys = await db.surveys.count_documents({"karyakarta_id": {"$in": karyakarta_ids}})
    
    # Karyakarta performance
    karyakarta_stats = []
    for k in karyakartas:
        k_id = str(k["_id"])
        assigned = await db.voters.count_documents({"assigned_to": k_id})
        k_visited = await db.voters.count_documents({"assigned_to": k_id, "visited_status": True})
        k_surveys = await db.surveys.count_documents({"karyakarta_id": k_id})
        
        karyakarta_stats.append({
            "id": k_id,
            "name": k["full_name"],
            "assigned_voters": assigned,
            "visited_voters": k_visited,
            "surveys_completed": k_surveys,
            "coverage": (k_visited / assigned * 100) if assigned > 0 else 0
        })
    
    return {
        "total_voters": total_voters,
        "assigned_voters": assigned_voters,
        "visited_voters": visited,
        "voted_voters": voted,
        "total_karyakartas": len(karyakartas),
        "total_surveys": total_surveys,
        "karyakarta_performance": karyakarta_stats
    }

@router.get("/super-admin")
async def get_super_admin_dashboard(
    current_user: dict = Depends(require_role(["super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get super admin dashboard data"""
    # Overall stats
    total_voters = await db.voters.count_documents({})
    visited = await db.voters.count_documents({"visited_status": True})
    voted = await db.voters.count_documents({"voted_status": True})
    total_surveys = await db.surveys.count_documents({})
    
    # User counts
    total_admins = await db.users.count_documents({"role": "admin"})
    total_karyakartas = await db.users.count_documents({"role": "karyakarta"})
    
    # Booth-wise performance
    booth_pipeline = [
        {"$group": {
            "_id": "$booth_number",
            "total": {"$sum": 1},
            "visited": {"$sum": {"$cond": ["$visited_status", 1, 0]}},
            "voted": {"$sum": {"$cond": ["$voted_status", 1, 0]}}
        }},
        {"$sort": {"_id": 1}}
    ]
    booth_stats = await db.voters.aggregate(booth_pipeline).to_list(1000)
    
    # Favor score distribution
    favor_pipeline = [
        {"$bucket": {
            "groupBy": "$favor_score",
            "boundaries": [0, 20, 40, 60, 80, 100],
            "default": "Other",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    favor_dist = await db.voters.aggregate(favor_pipeline).to_list(10)
    
    return {
        "total_voters": total_voters,
        "visited_voters": visited,
        "voted_voters": voted,
        "visit_percentage": (visited / total_voters * 100) if total_voters > 0 else 0,
        "turnout_percentage": (voted / total_voters * 100) if total_voters > 0 else 0,
        "total_surveys": total_surveys,
        "total_admins": total_admins,
        "total_karyakartas": total_karyakartas,
        "booth_performance": booth_stats,
        "favor_score_distribution": favor_dist
    }
