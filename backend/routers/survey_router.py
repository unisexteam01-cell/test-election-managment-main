from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List
import logging

from models import (
    SurveyTemplate, SurveyTemplateCreate, Survey, SurveySubmit
)
from auth import get_current_user, require_role
from database import get_database

router = APIRouter(prefix="/surveys", tags=["surveys"])
logger = logging.getLogger(__name__)

@router.post("/templates", response_model=SurveyTemplate)
async def create_survey_template(
    template_data: SurveyTemplateCreate,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a survey template"""
    template_dict = template_data.model_dump()
    template_dict["created_by"] = current_user["sub"]
    template_dict["created_at"] = datetime.utcnow()
    template_dict["active_status"] = True
    
    result = await db.survey_templates.insert_one(template_dict)
    template_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"Survey template '{template_data.template_name}' created by {current_user['username']}")
    return SurveyTemplate(**template_dict)

@router.get("/templates", response_model=List[SurveyTemplate])
async def get_survey_templates(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all survey templates"""
    query = {"active_status": True}
    
    # Super Admin sees all, Admin sees default + their own
    if current_user["role"] == "admin":
        query["$or"] = [
            {"is_default": True},
            {"created_by": current_user["sub"]}
        ]
    elif current_user["role"] == "karyakarta":
        # Karyakarta sees default templates only
        query["is_default"] = True
    
    templates = await db.survey_templates.find(query).to_list(100)
    
    for template in templates:
        template["_id"] = str(template["_id"])
    
    return [SurveyTemplate(**t) for t in templates]

@router.get("/templates/{template_id}", response_model=SurveyTemplate)
async def get_survey_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific survey template"""
    template = await db.survey_templates.find_one({"_id": ObjectId(template_id)})
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template["_id"] = str(template["_id"])
    return SurveyTemplate(**template)

@router.post("/submit", response_model=Survey)
async def submit_survey(
    survey_data: SurveySubmit,
    current_user: dict = Depends(require_role(["karyakarta", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Submit a completed survey"""
    # Verify voter exists
    voter = await db.voters.find_one({"_id": ObjectId(survey_data.voter_id)})
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # Verify template exists
    template = await db.survey_templates.find_one({"_id": ObjectId(survey_data.template_id)})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create survey
    survey_dict = survey_data.model_dump()
    survey_dict["karyakarta_id"] = current_user["sub"]
    survey_dict["timestamp"] = datetime.utcnow()
    survey_dict["favor_score_impact"] = 0.0  # Will be calculated
    
    result = await db.surveys.insert_one(survey_dict)
    survey_dict["_id"] = str(result.inserted_id)
    
    # Update voter's survey history
    await db.voters.update_one(
        {"_id": ObjectId(survey_data.voter_id)},
        {
            "$push": {"survey_history": str(result.inserted_id)},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Update user stats
    await db.users.update_one(
        {"_id": ObjectId(current_user["sub"])},
        {"$inc": {"activity_stats.surveys_completed": 1}}
    )
    
    logger.info(f"Survey submitted for voter {voter.get('full_name')} by {current_user['username']}")
    return Survey(**survey_dict)

@router.get("/voter/{voter_id}", response_model=List[Survey])
async def get_voter_surveys(
    voter_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all surveys for a voter"""
    surveys = await db.surveys.find({"voter_id": voter_id}).sort("timestamp", -1).to_list(100)
    
    for survey in surveys:
        survey["_id"] = str(survey["_id"])
    
    return [Survey(**s) for s in surveys]

@router.get("/my-surveys", response_model=List[Survey])
async def get_my_surveys(
    current_user: dict = Depends(require_role(["karyakarta"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all surveys submitted by current karyakarta"""
    surveys = await db.surveys.find({"karyakarta_id": current_user["sub"]}).sort("timestamp", -1).to_list(100)
    
    for survey in surveys:
        survey["_id"] = str(survey["_id"])
    
    return [Survey(**s) for s in surveys]

@router.get("/statistics")
async def get_survey_statistics(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get survey statistics"""
    query = {}
    if current_user["role"] == "karyakarta":
        query["karyakarta_id"] = current_user["sub"]
    
    total_surveys = await db.surveys.count_documents(query)
    
    # Surveys by template
    template_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$template_id", "count": {"$sum": 1}}}
    ]
    by_template = await db.surveys.aggregate(template_pipeline).to_list(20)
    
    # Recent surveys
    recent = await db.surveys.find(query).sort("timestamp", -1).limit(10).to_list(10)
    for survey in recent:
        survey["_id"] = str(survey["_id"])
    
    return {
        "total_surveys": total_surveys,
        "by_template": by_template,
        "recent_surveys": recent
    }
