from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import logging

from models import Task, TaskCreate, TaskStatus
from auth import get_current_user, require_role
from database import get_database

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=Task)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(require_role(["admin", "super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new task"""
    # Verify assigned user exists
    user = await db.users.find_one({"_id": ObjectId(task_data.assigned_to)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    task_dict = task_data.model_dump()
    task_dict["assigned_by"] = current_user["sub"]
    task_dict["status"] = TaskStatus.PENDING
    task_dict["completion_percentage"] = 0.0
    task_dict["created_at"] = datetime.utcnow()
    
    result = await db.tasks.insert_one(task_dict)
    task_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"Task assigned to {user['username']} by {current_user['username']}")
    return Task(**task_dict)

@router.get("/assigned-to-me", response_model=List[Task])
async def get_my_tasks(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get tasks assigned to current user"""
    query = {"assigned_to": current_user["sub"]}
    if status:
        query["status"] = status
    
    tasks = await db.tasks.find(query).sort("created_at", -1).to_list(100)
    
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return [Task(**t) for t in tasks]

@router.put("/{task_id}", response_model=Task)
async def update_task_status(
    task_id: str,
    status: TaskStatus,
    completion_percentage: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update task status"""
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check authorization
    if task["assigned_to"] != current_user["sub"] and current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {"status": status}
    if completion_percentage is not None:
        update_data["completion_percentage"] = completion_percentage
    if status == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
        update_data["completion_percentage"] = 100.0
    
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )
    
    updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    updated_task["_id"] = str(updated_task["_id"])
    
    return Task(**updated_task)
