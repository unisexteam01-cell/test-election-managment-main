from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import asyncio
from backend.database import connect_to_mongo, get_database
import datetime

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return payload

def require_role(allowed_roles: list):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

async def create_user(db, username: str, password: str, role: str):
    """Create a user with the specified role and return their credentials"""
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        print(f"User with username '{username}' already exists.")
        return {"user_id": str(existing_user["_id"]), "username": username, "password": password, "role": role}

    truncated_password = password[:72]  # Truncate password to 72 characters
    hashed_password = get_password_hash(truncated_password)
    user = {
        "username": username,
        "email": f"{username}@example.com",  # Add unique email field
        "password": hashed_password,
        "role": role,
        "created_at": datetime.datetime.now(datetime.timezone.utc)  # Use timezone-aware datetime
    }
    result = await db.users.insert_one(user)
    return {"user_id": str(result.inserted_id), "username": username, "password": truncated_password, "role": role}

async def create_all_roles():
    await connect_to_mongo()
    db = await get_database()

    roles = ["admin", "super-admin", "karyakarta"]
    credentials = []

    for role in roles:
        username = f"{role}_user"
        password = f"{role}_pass123"
        user = await create_user(db, username, password, role)
        credentials.append(user)

    for credential in credentials:
        print(f"Username: {credential['username']}, Password: {credential['password']}, Role: {credential['role']}")

if __name__ == "__main__":
    asyncio.run(create_all_roles())
