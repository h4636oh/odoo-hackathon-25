from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserLogin, UserResponse, Token
from models.company import CompanyCreate, CompanyResponse, CompanySignup
from utils.auth import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token
)
from utils.database import DatabaseManager
from database import database
import uuid
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# Initialize database manager
db_manager = DatabaseManager(database)

@router.post("/admin/signup", response_model=Token)
async def admin_signup(company_data: CompanySignup):
    """Admin signup - create a new company."""
    # Check if company already exists
    existing_company = await db_manager.get_company_by_email(company_data.email)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this email already exists"
        )
    
    # Create company
    company_dict = {
        "company_name": company_data.company_name,
        "country": company_data.country,
        "admin_email": company_data.email,
        "admin_password_hash": get_password_hash(company_data.password)
    }
    
    company = await db_manager.create_company(company_dict)
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": company["company_id"]})
    refresh_token = create_refresh_token(data={"sub": company["company_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/admin/signin", response_model=Token)
async def admin_signin(login_data: UserLogin):
    """Admin signin."""
    # Find company by admin email
    company = await db_manager.get_company_by_email(login_data.email)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, company["admin_password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": company["company_id"]})
    refresh_token = create_refresh_token(data={"sub": company["company_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/user/signin", response_model=Token)
async def user_signin(login_data: UserLogin):
    """User signin."""
    # Find user by email
    user = await db_manager.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["user_id"]})
    refresh_token = create_refresh_token(data={"sub": user["user_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
