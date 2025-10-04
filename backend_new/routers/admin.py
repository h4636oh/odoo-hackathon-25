from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserCreate, UserResponse, UserUpdate
from models.request import RequestResponse, RequestDetailResponse
from models.rule import RuleCreate, RuleResponse
from utils.auth import get_current_admin_user
from utils.database import DatabaseManager
from database import database, companies_collection
import uuid
from typing import List

router = APIRouter()

# Initialize database manager
db_manager = DatabaseManager(database)

# Helper function to get current admin
async def get_current_admin():
    return await get_current_admin_user(companies_collection=companies_collection)

@router.post("/create_user", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new user (employee/manager)."""
    # Check if user already exists
    existing_user = await db_manager.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user_dict = user_data.dict()
    user_dict["password_hash"] = get_password_hash(user_data.password)
    user_dict["company_id"] = current_admin["company_id"]
    del user_dict["password"]
    
    user = await db_manager.create_user(user_dict)
    
    return {"message": "User created successfully", "user_id": user["user_id"]}

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_admin: dict = Depends(get_current_admin)
):
    """Get all users for the company."""
    users = await db_manager.get_all_users(current_admin["company_id"])
    return users

@router.post("/change_role/{user_id}", response_model=dict)
async def change_user_role(
    user_id: str,
    role_data: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """Change user role."""
    user = await db_manager.get_user_by_id(user_id)
    if not user or user["company_id"] != current_admin["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db_manager.update_user(user_id, {"role": role_data["role"]})
    return {"message": "User role changed successfully"}

@router.post("/change_manager/{user_id}", response_model=dict)
async def change_user_manager(
    user_id: str,
    manager_data: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """Change user's manager."""
    user = await db_manager.get_user_by_id(user_id)
    if not user or user["company_id"] != current_admin["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    manager_id = manager_data.get("manager_id")
    if manager_id:
        manager = await db_manager.get_user_by_id(manager_id)
        if not manager or manager["company_id"] != current_admin["company_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )
    
    await db_manager.update_user(user_id, {"manager_id": manager_id})
    return {"message": "User manager changed successfully"}

@router.post("/send_password/{user_id}", response_model=dict)
async def send_password_reset(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Send password reset email to user."""
    user = await db_manager.get_user_by_id(user_id)
    if not user or user["company_id"] != current_admin["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # In a real application, you would send an email here
    # For now, we'll just return a success message
    return {"message": "Password reset email sent successfully"}

@router.get("/requests", response_model=List[RequestResponse])
async def get_all_requests(
    current_admin: dict = Depends(get_current_admin)
):
    """Get all requests for the company."""
    requests = await db_manager.get_all_requests(current_admin["company_id"])
    return requests

@router.get("/requests/{request_id}", response_model=RequestDetailResponse)
async def get_request_details(
    request_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get detailed information about a specific request."""
    request = await db_manager.get_request_by_id(request_id)
    if not request or request["company_id"] != current_admin["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    return request

@router.post("/generate_request_rules/{request_id}", response_model=dict)
async def generate_request_rules(
    request_id: str,
    rule_data: RuleCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Generate approval rules for a request."""
    # Check if request exists
    request = await db_manager.get_request_by_id(request_id)
    if not request or request["company_id"] != current_admin["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Create rule
    rule_dict = rule_data.dict()
    rule_dict["company_id"] = current_admin["company_id"]
    
    rule = await db_manager.create_rule(rule_dict)
    
    # Update request status to pending
    await db_manager.update_request(request_id, {
        "status": "pending",
        "rule_description": rule_data.rule_description
    })
    
    return {"message": "Rule created successfully", "rule_id": rule["rule_id"]}

@router.get("/expenses", response_model=dict)
async def get_expense_summary(
    current_admin: dict = Depends(get_current_admin)
):
    """Get expense summary for the company."""
    summary = await db_manager.get_expense_summary(current_admin["company_id"])
    return summary
