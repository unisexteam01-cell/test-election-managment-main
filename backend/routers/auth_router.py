from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import logging

from models import (
    User, UserCreate, UserLogin, Token, UserRole, ActivityStats
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_role
)
from database import get_database

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user (Super Admin creates Admin, Admin creates Karyakarta)
    """
    # Check permissions
    if current_user["role"] == "super_admin" and user_data.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin can only create Admin users"
        )
    
    if current_user["role"] == "admin" and user_data.role not in [UserRole.KARYAKARTA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin can only create Karyakarta users"
        )
    
    # Check if username or email already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"username": user_data.username},
            {"email": user_data.email}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user document
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["password_hash"] = get_password_hash(user_data.password)
    user_dict["created_by"] = current_user["sub"]
    user_dict["created_at"] = datetime.utcnow()
    user_dict["last_login"] = None
    user_dict["active_status"] = True
    user_dict["activity_stats"] = ActivityStats().model_dump()
    
    # Set assigned_admin_id for Karyakarta
    if user_data.role == UserRole.KARYAKARTA:
        user_dict["assigned_admin_id"] = current_user["sub"]
    
    # Insert into database
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"User {user_data.username} registered successfully by {current_user['username']}")
    return User(**user_dict)

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login user and return JWT token
    """
    # Find user by username
    user = await db.users.find_one({"username": login_data.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user.get("active_status", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    token_data = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "email": user["email"]
    }
    access_token = create_access_token(token_data)
    
    # Prepare user response
    user["_id"] = str(user["_id"])
    user.pop("password_hash", None)
    
    logger.info(f"User {login_data.username} logged in successfully")
    return Token(access_token=access_token, user=User(**user))

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current authenticated user information
    """
    user = await db.users.find_one({"_id": ObjectId(current_user["sub"])})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    user.pop("password_hash", None)
    return User(**user)

@router.get("/users", response_model=list[User])
async def get_users(
    role: str = None,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get list of users (filtered by role if provided)
    Super Admin sees all, Admin sees only their Karyakartas
    """
    query = {}
    
    if current_user["role"] == "admin":
        # Admin can only see their own Karyakartas
        query["assigned_admin_id"] = current_user["sub"]
    
    if role:
        query["role"] = role
    
    users = await db.users.find(query).to_list(1000)
    
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
    
    return [User(**user) for user in users]

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(require_role(["super_admin", "admin"])),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Deactivate a user account
    """
    # Check permissions
    user_to_deactivate = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user_to_deactivate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Admin can only deactivate their own Karyakartas
    if current_user["role"] == "admin":
        if user_to_deactivate.get("assigned_admin_id") != current_user["sub"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to deactivate this user"
            )
    
    # Update user status
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"active_status": False}}
    )
    
    return {"message": "User deactivated successfully"}

@router.post("/create-super-admin", response_model=User)
async def create_initial_super_admin(
    username: str = "superadmin",
    password: str = "admin123",
    email: str = "admin@political.com",
    full_name: str = "Super Admin",
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create initial super admin account (should be disabled in production)
    This is a utility endpoint for initial setup
    """
    # Check if any super admin exists
    existing_admin = await db.users.find_one({"role": UserRole.SUPER_ADMIN})
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super Admin already exists"
        )
    
    # Create super admin
    user_dict = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "phone": None,
        "role": UserRole.SUPER_ADMIN,
        "password_hash": get_password_hash(password),
        "created_by": None,
        "assigned_admin_id": None,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "active_status": True,
        "activity_stats": ActivityStats().model_dump()
    }
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    user_dict.pop("password_hash")
    
    logger.info(f"Super Admin created: {username}")
    return User(**user_dict)
