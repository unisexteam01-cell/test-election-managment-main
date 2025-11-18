from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import pandas as pd
import io
import logging
from typing import Dict, List

from auth import get_current_user, require_role
from database import get_database

router = APIRouter(prefix="/import", tags=["import"])
logger = logging.getLogger(__name__)

@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload CSV file and return preview with column headers"""
    try:
        contents = await file.read()
        
        # Try to read as CSV
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except:
            # Try Excel
            df = pd.read_excel(io.BytesIO(contents))
        
        # Get column headers
        columns = df.columns.tolist()
        
        # Get first 5 rows as preview
        preview = df.head(5).to_dict('records')
        
        # Store temporary file info in database
        import_session = {
            "uploaded_by": current_user["sub"],
            "filename": file.filename,
            "total_rows": len(df),
            "columns": columns,
            "preview": preview,
            "status": "pending_mapping",
            "created_at": datetime.utcnow()
        }
        
        result = await db.import_sessions.insert_one(import_session)
        import_session["_id"] = str(result.inserted_id)
        
        # Store the dataframe as JSON temporarily
        df_json = df.to_dict('records')
        await db.temp_imports.insert_one({
            "session_id": str(result.inserted_id),
            "data": df_json,
            "created_at": datetime.utcnow()
        })
        
        return {
            "session_id": str(result.inserted_id),
            "columns": columns,
            "preview": preview,
            "total_rows": len(df)
        }
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/map-columns")
async def map_columns(
    session_id: str,
    column_mapping: Dict[str, str],
    admin_id: str,
    current_user: dict = Depends(require_role(["super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Map CSV columns to voter fields and import data for specific admin"""
    try:
        # Get admin user
        admin = await db.users.find_one({"_id": ObjectId(admin_id)})
        if not admin or admin["role"] != "admin":
            raise HTTPException(status_code=400, detail="Invalid admin user")
        
        # Get temp data
        temp_data = await db.temp_imports.find_one({"session_id": session_id})
        if not temp_data:
            raise HTTPException(status_code=404, detail="Import session not found")
        
        df_data = temp_data["data"]
        
        # Process and import voters
        imported_count = 0
        error_count = 0
        errors = []
        
        for idx, row in enumerate(df_data):
            try:
                # Map columns
                voter_data = {}
                
                # Required fields
                name_en = row.get(column_mapping.get("name_english", ""), "")
                name_mr = row.get(column_mapping.get("name_marathi", ""), "")
                voter_data["name"] = name_en or name_mr
                
                # Age
                age_field = column_mapping.get("age")
                if age_field:
                    try:
                        voter_data["age"] = int(row.get(age_field, 18))
                    except:
                        voter_data["age"] = 18
                
                # Gender
                gender_field = column_mapping.get("gender")
                if gender_field:
                    gender_val = str(row.get(gender_field, "")).lower()
                    if "male" in gender_val or "पु" in gender_val:
                        voter_data["gender"] = "male"
                    elif "female" in gender_val or "स्त्री" in gender_val:
                        voter_data["gender"] = "female"
                    else:
                        voter_data["gender"] = "other"
                else:
                    voter_data["gender"] = "male"
                
                # Area
                area_en = row.get(column_mapping.get("area_english", ""), "")
                area_mr = row.get(column_mapping.get("area_marathi", ""), "")
                voter_data["area"] = area_en or area_mr or "Unknown"
                
                # Optional fields
                if "booth_number" in column_mapping:
                    voter_data["booth_number"] = str(row.get(column_mapping["booth_number"], "1"))
                else:
                    voter_data["booth_number"] = "1"
                
                if "ward" in column_mapping:
                    voter_data["ward"] = str(row.get(column_mapping["ward"], ""))
                
                if "phone" in column_mapping:
                    voter_data["phone"] = str(row.get(column_mapping["phone"], ""))
                
                if "caste" in column_mapping:
                    voter_data["caste"] = str(row.get(column_mapping["caste"], ""))
                
                if "address" in column_mapping:
                    voter_data["address"] = str(row.get(column_mapping["address"], ""))
                
                # Set defaults
                voter_data["full_name"] = voter_data["name"]
                voter_data["favor_score"] = 50.0
                voter_data["favor_category"] = "neutral"
                voter_data["visited_status"] = False
                voter_data["voted_status"] = False
                voter_data["visit_count"] = 0
                voter_data["tags"] = []
                voter_data["notes"] = []
                voter_data["survey_history"] = []
                voter_data["created_at"] = datetime.utcnow()
                voter_data["updated_at"] = datetime.utcnow()
                voter_data["imported_at"] = datetime.utcnow()
                
                # IMPORTANT: Assign to admin
                voter_data["admin_id"] = admin_id
                voter_data["assigned_to"] = None  # Not assigned to karyakarta yet
                
                # Insert voter
                await db.voters.insert_one(voter_data)
                imported_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({
                    "row_number": idx + 1,
                    "error_message": str(e),
                    "row_data": row
                })
        
        # Update import session
        await db.import_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$set": {
                    "status": "completed",
                    "imported_count": imported_count,
                    "error_count": error_count,
                    "errors": errors[:100],  # Store first 100 errors
                    "admin_id": admin_id,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Clean up temp data
        await db.temp_imports.delete_one({"session_id": session_id})
        
        logger.info(f"Imported {imported_count} voters for admin {admin['username']}")
        
        return {
            "message": "Import completed",
            "imported_count": imported_count,
            "error_count": error_count,
            "errors": errors[:10]  # Return first 10 errors
        }
        
    except Exception as e:
        logger.error(f"Error mapping columns: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions")
async def get_import_sessions(
    current_user: dict = Depends(require_role(["super_admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all import sessions"""
    sessions = await db.import_sessions.find().sort("created_at", -1).limit(50).to_list(50)
    
    for session in sessions:
        session["_id"] = str(session["_id"])
    
    return sessions
