from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import pandas as pd
import io
import logging

from models import (
    Voter, VoterCreate, VoterFilter, VoterBulkUpdate, VoterAssignment, Gender
)
from auth import get_current_user, require_role
from database import get_database

router = APIRouter(prefix="/voters", tags=["voters"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=Voter, status_code=status.HTTP_201_CREATED)
async def create_voter(
    voter_data: VoterCreate,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new voter"""
    voter_dict = voter_data.model_dump()
    voter_dict["created_at"] = datetime.utcnow()
    voter_dict["updated_at"] = datetime.utcnow()
    voter_dict["favor_score"] = 50.0
    voter_dict["favor_category"] = "neutral"
    voter_dict["visited_status"] = False
    voter_dict["voted_status"] = False
    voter_dict["visit_count"] = 0
    voter_dict["tags"] = []
    voter_dict["notes"] = []
    voter_dict["survey_history"] = []
    
    # Generate full_name if not provided
    if not voter_dict.get("full_name"):
        parts = [voter_dict["name"]]
        if voter_dict.get("surname"):
            parts.append(voter_dict["surname"])
        voter_dict["full_name"] = " ".join(parts)
    
    result = await db.voters.insert_one(voter_dict)
    voter_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"Voter {voter_dict['full_name']} created by {current_user['username']}")
    return Voter(**voter_dict)

@router.get("/", response_model=dict)
async def get_voters(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    gender: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    area: Optional[str] = None,
    ward: Optional[str] = None,
    booth_number: Optional[str] = None,
    caste: Optional[str] = None,
    family_id: Optional[str] = None,
    favor_score_min: Optional[float] = None,
    favor_score_max: Optional[float] = None,
    visited: Optional[bool] = None,
    voted: Optional[bool] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get voters with advanced filtering and pagination"""
    query = {}
    
    # Role-based filtering - CRITICAL: Data isolation
    if current_user["role"] == "karyakarta":
        # Karyakarta sees only assigned voters
        query["assigned_to"] = current_user["sub"]
    elif current_user["role"] == "admin":
        # Admin sees only their voters (assigned by Super Admin)
        query["admin_id"] = current_user["sub"]
        if assigned_to:
            # Can filter by karyakarta within their team
            query["assigned_to"] = assigned_to
    # Super Admin sees all voters (no query restriction)
    
    # Text search
    if search:
        query["$text"] = {"$search": search}
    
    # Filters
    if gender:
        query["gender"] = gender
    if age_min is not None or age_max is not None:
        query["age"] = {}
        if age_min is not None:
            query["age"]["$gte"] = age_min
        if age_max is not None:
            query["age"]["$lte"] = age_max
    if area:
        query["area"] = area
    if ward:
        query["ward"] = ward
    if booth_number:
        query["booth_number"] = booth_number
    if caste:
        query["caste"] = caste
    if family_id:
        query["family_id"] = family_id
    if favor_score_min is not None or favor_score_max is not None:
        query["favor_score"] = {}
        if favor_score_min is not None:
            query["favor_score"]["$gte"] = favor_score_min
        if favor_score_max is not None:
            query["favor_score"]["$lte"] = favor_score_max
    if visited is not None:
        query["visited_status"] = visited
    if voted is not None:
        query["voted_status"] = voted
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    # Get total count
    total = await db.voters.count_documents(query)
    
    # Pagination
    skip = (page - 1) * limit
    
    # Get voters
    cursor = db.voters.find(query).skip(skip).limit(limit).sort("created_at", -1)
    voters = await cursor.to_list(length=limit)
    
    for voter in voters:
        voter["_id"] = str(voter["_id"])
    
    return {
        "voters": [Voter(**v) for v in voters],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{voter_id}", response_model=Voter)
async def get_voter(
    voter_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific voter"""
    voter = await db.voters.find_one({"_id": ObjectId(voter_id)})
    
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # Check access rights
    if current_user["role"] == "karyakarta":
        if voter.get("assigned_to") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this voter")
    
    voter["_id"] = str(voter["_id"])
    return Voter(**voter)

@router.put("/{voter_id}", response_model=Voter)
async def update_voter(
    voter_id: str,
    voter_data: VoterCreate,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a voter"""
    voter = await db.voters.find_one({"_id": ObjectId(voter_id)})
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    update_data = voter_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Update full_name if name/surname changed
    if "name" in update_data or "surname" in update_data:
        name = update_data.get("name", voter.get("name"))
        surname = update_data.get("surname", voter.get("surname", ""))
        parts = [name]
        if surname:
            parts.append(surname)
        update_data["full_name"] = " ".join(parts)
    
    await db.voters.update_one(
        {"_id": ObjectId(voter_id)},
        {"$set": update_data}
    )
    
    updated_voter = await db.voters.find_one({"_id": ObjectId(voter_id)})
    updated_voter["_id"] = str(updated_voter["_id"])
    
    return Voter(**updated_voter)

@router.delete("/{voter_id}")
async def delete_voter(
    voter_id: str,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a voter"""
    result = await db.voters.delete_one({"_id": ObjectId(voter_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    return {"message": "Voter deleted successfully"}

@router.post("/assign")
async def assign_voters(
    assignment: VoterAssignment,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign voters to a karyakarta"""
    # Verify karyakarta exists
    karyakarta = await db.users.find_one({"_id": ObjectId(assignment.karyakarta_id)})
    if not karyakarta or karyakarta["role"] != "karyakarta":
        raise HTTPException(status_code=400, detail="Invalid karyakarta")
    
    # Update voters
    result = await db.voters.update_many(
        {"_id": {"$in": [ObjectId(vid) for vid in assignment.voter_ids]}},
        {
            "$set": {
                "assigned_to": assignment.karyakarta_id,
                "assigned_by": current_user["sub"],
                "assigned_date": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"{result.modified_count} voters assigned to {karyakarta['username']}")
    return {"message": f"{result.modified_count} voters assigned successfully"}

@router.post("/bulk-update")
async def bulk_update_voters(
    bulk_update: VoterBulkUpdate,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Bulk update voters"""
    updates = bulk_update.updates
    updates["updated_at"] = datetime.utcnow()
    
    result = await db.voters.update_many(
        {"_id": {"$in": [ObjectId(vid) for vid in bulk_update.voter_ids]}},
        {"$set": updates}
    )
    
    return {"message": f"{result.modified_count} voters updated successfully"}

@router.post("/{voter_id}/mark-visited")
async def mark_voter_visited(
    voter_id: str,
    current_user: dict = Depends(require_role(["karyakarta", "admin", "super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark voter as visited"""
    update_data = {
        "visited_status": True,
        "visited_by": current_user["sub"],
        "visited_date": datetime.utcnow(),
        "$inc": {"visit_count": 1}
    }
    
    result = await db.voters.update_one(
        {"_id": ObjectId(voter_id)},
        {"$set": {k: v for k, v in update_data.items() if k != "$inc"}, "$inc": update_data["$inc"]}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # Update user stats
    await db.users.update_one(
        {"_id": ObjectId(current_user["sub"])},
        {"$inc": {"activity_stats.voters_visited": 1}}
    )
    
    return {"message": "Voter marked as visited"}

@router.post("/{voter_id}/mark-voted")
async def mark_voter_voted(
    voter_id: str,
    current_user: dict = Depends(require_role(["karyakarta", "admin", "super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark voter as voted (election day)"""
    result = await db.voters.update_one(
        {"_id": ObjectId(voter_id)},
        {
            "$set": {
                "voted_status": True,
                "voted_timestamp": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    return {"message": "Voter marked as voted"}

@router.get("/stats/summary")
async def get_voter_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get voter statistics"""
    query = {}
    if current_user["role"] == "karyakarta":
        query["assigned_to"] = current_user["sub"]
    
    total = await db.voters.count_documents(query)
    visited = await db.voters.count_documents({**query, "visited_status": True})
    voted = await db.voters.count_documents({**query, "voted_status": True})
    
    # Gender distribution
    gender_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
    ]
    gender_dist = await db.voters.aggregate(gender_pipeline).to_list(10)
    
    # Age distribution
    age_pipeline = [
        {"$match": query},
        {"$bucket": {
            "groupBy": "$age",
            "boundaries": [18, 25, 35, 45, 55, 65, 100],
            "default": "Other",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    age_dist = await db.voters.aggregate(age_pipeline).to_list(10)
    
    return {
        "total": total,
        "visited": visited,
        "voted": voted,
        "pending": total - visited,
        "visit_percentage": (visited / total * 100) if total > 0 else 0,
        "turnout_percentage": (voted / total * 100) if total > 0 else 0,
        "gender_distribution": gender_dist,
        "age_distribution": age_dist
    }


@router.get("/export")
async def export_voters(
    search: Optional[str] = None,
    gender: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    area: Optional[str] = None,
    ward: Optional[str] = None,
    booth_number: Optional[str] = None,
    caste: Optional[str] = None,
    family_id: Optional[str] = None,
    visited: Optional[bool] = None,
    voted: Optional[bool] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Export filtered voters to CSV (returns CSV file)"""
    query = {}
    if current_user["role"] == "karyakarta":
        query["assigned_to"] = current_user["sub"]
    elif current_user["role"] == "admin":
        query["admin_id"] = current_user["sub"]
        if assigned_to:
            query["assigned_to"] = assigned_to

    if search:
        query["$text"] = {"$search": search}
    if gender:
        query["gender"] = gender
    if age_min is not None or age_max is not None:
        query["age"] = {}
        if age_min is not None:
            query["age"]["$gte"] = age_min
        if age_max is not None:
            query["age"]["$lte"] = age_max
    if area:
        query["area"] = area
    if ward:
        query["ward"] = ward
    if booth_number:
        query["booth_number"] = booth_number
    if caste:
        query["caste"] = caste
    if family_id:
        query["family_id"] = family_id
    if visited is not None:
        query["visited_status"] = visited
    if voted is not None:
        query["voted_status"] = voted
    if assigned_to:
        query["assigned_to"] = assigned_to

    cursor = db.voters.find(query)
    voters = await cursor.to_list(length=10000)

    # Prepare CSV
    import pandas as pd
    df = pd.DataFrame(voters)
    # Drop Mongo internal fields and prepare human-readable columns
    if "_id" in df.columns:
        df["id"] = df["_id"].astype(str)
        df = df.drop(columns=["_id"])

    csv_bytes = df.to_csv(index=False).encode("utf-8")

    from fastapi.responses import StreamingResponse
    import io
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=voters_export.csv"})
