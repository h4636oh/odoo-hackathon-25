from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserResponse
from models.request import RequestCreate, RequestResponse, RequestDetailResponse
from utils.auth import get_current_user
from utils.database import DatabaseManager
from database import database, users_collection
from typing import List

router = APIRouter()

# Initialize database manager
db_manager = DatabaseManager(database)

# Helper function to get current user
async def get_current_user_helper():
    return await get_current_user(users_collection=users_collection)

@router.get("/requests", response_model=List[RequestResponse])
async def get_user_requests(
    current_user: dict = Depends(get_current_user_helper)
):
    """Get all requests created by the current user."""
    requests = await db_manager.get_requests_by_user(current_user["user_id"])
    return requests

@router.post("/create_request", response_model=dict)
async def create_request(
    request_data: RequestCreate,
    current_user: dict = Depends(get_current_user_helper)
):
    """Create a new expense request."""
    # Create request
    request_dict = request_data.dict()
    request_dict["company_id"] = current_user["company_id"]
    
    request = await db_manager.create_request(request_dict)
    
    return {"message": "Request created successfully", "request_id": request["request_id"]}

@router.post("/approve_request/{request_id}", response_model=dict)
async def approve_request(
    request_id: str,
    current_user: dict = Depends(get_current_user_helper)
):
    """Approve a request."""
    # Get request details
    request = await db_manager.get_request_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Get approval rule
    rule = await db_manager.get_rule_by_request_id(request_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approval rule found for this request"
        )
    
    # Check if user is authorized to approve
    if current_user["user_id"] not in rule["approvers"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to approve this request"
        )
    
    # Add user to approved list if not already there
    if current_user["user_id"] not in request.get("approved_by", []):
        approved_by = request.get("approved_by", [])
        approved_by.append(current_user["user_id"])
        
        # Check if approval criteria is met
        total_approvers = len(rule["approvers"])
        approved_count = len(approved_by)
        required_approvals = max(1, int(total_approvers * rule["percentage_required"] / 100))
        
        # Check compulsory approvers
        compulsory_approved = all(
            approver in approved_by 
            for approver in rule["compulsory_approvers"]
        )
        
        if approved_count >= required_approvals and compulsory_approved:
            # Request is fully approved
            await db_manager.update_request(request_id, {
                "status": "approved",
                "approved_by": approved_by
            })
        else:
            # Still pending more approvals
            await db_manager.update_request(request_id, {
                "approved_by": approved_by
            })
    
    return {"message": "Request approved successfully"}

@router.post("/reject_request/{request_id}", response_model=dict)
async def reject_request(
    request_id: str,
    current_user: dict = Depends(get_current_user_helper)
):
    """Reject a request."""
    # Get request details
    request = await db_manager.get_request_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Get approval rule
    rule = await db_manager.get_rule_by_request_id(request_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approval rule found for this request"
        )
    
    # Check if user is authorized to reject
    if current_user["user_id"] not in rule["approvers"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to reject this request"
        )
    
    # Reject the request
    await db_manager.update_request(request_id, {
        "status": "rejected",
        "rejected_by": current_user["user_id"]
    })
    
    return {"message": "Request rejected successfully"}

@router.get("/team_expense", response_model=dict)
async def get_team_expense(
    current_user: dict = Depends(get_current_user_helper)
):
    """Get team expense summary for managers."""
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view team expenses"
        )
    
    summary = await db_manager.get_team_expense_summary(current_user["user_id"])
    return summary
