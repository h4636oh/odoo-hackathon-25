import os
import random
import string
from datetime import timedelta

import httpx
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, status, Body, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

import auth
import database
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from database import db
from mailer import send_email

app = FastAPI()

# Create separate routers for admin and user
admin_router = APIRouter()
user_router = APIRouter()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# region Models
class Admin(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    country: str


class User(BaseModel):
    name: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class Request(BaseModel):
    requestor: str
    description: str
    expense_date: str
    category: str
    paidBy: str
    payment_Currency: str
    payment_Amount: float
    remarks: str
    status: str = "submitted"


class RequestRule(BaseModel):
    rule_description: str
    temp_manager: str | None = None
    manager_required: bool
    approvers: list[str]
    compulsory_Approvers: list[str]
    sequential: bool
    percentage_Required: int


# endregion Models

# region Helper Functions
def get_password_hash(password):
    # bcrypt has a 72-character limit for passwords. Truncate to avoid errors.
    return pwd_context.hash(password[:72])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_currency_for_country(country_name: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://restcountries.com/v3.1/all?fields=name,currencies")
            response.raise_for_status()
            countries = response.json()
            for country in countries:
                if country["name"]["common"].lower() == country_name.lower():
                    currency_code = list(country["currencies"].keys())[0]
                    return currency_code
            return None
        except httpx.HTTPStatusError:
            return None

# endregion Helper Functions


# region Admin Routes
@admin_router.post("/admin/signup", response_model=Token)
async def admin_signup(form_data: Admin = Body(...)):
    existing_admin = await db["admins"].find_one({"Email": form_data.email})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    currency = await get_currency_for_country(form_data.country)
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find currency for country: {form_data.country}",
        )

    hashed_password = get_password_hash(form_data.password)
    admin_data = {
        "Name": form_data.company_name,
        "Email": form_data.email,
        "Password_hash": hashed_password,
        "Country": form_data.country,
        "Company_Currency": currency,
    }
    await db["admins"].insert_one(admin_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@admin_router.post("/admin/signin", response_model=Token)
async def admin_signin(form_data: OAuth2PasswordRequestForm = Depends()):
    admin = await db["admins"].find_one({"Email": form_data.username})
    if not admin or not verify_password(form_data.password, admin["Password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin["Email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@admin_router.post("/admin/create_user")
async def create_user(user: User, current_user: dict = Depends(get_current_user)):
    if await db["users"].find_one({"Email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hashed_password = get_password_hash(password)

    user_data = {
        "Name": user.name,
        "Email": user.email,
        "role": user.role,
        "Password_hash": hashed_password,
        "Approved_Requests": [],
        "Rejected_Requests": [],
        "Pending_Requests": [],
        "Manager": None,
        "To_Approve_Requests": [],
        "Has_Approved_Requests": [],
        "Has_Rejected_Requests": []
    }

    await db["users"].insert_one(user_data)

    # Send password to user's email
    subject = "Your Expense Tracker Account Details"
    body = f"Hello {user.name},\n\nYour account has been created.\nYour password is: {password}\n\nPlease change it after your first login."
    send_email(subject, body, user.email)

    return {"message": "User created successfully and password sent to email."}


@admin_router.get("/admin/users")
async def list_users(current_user: dict = Depends(get_current_user)):
    users_cursor = db["users"].find({})
    users_list = []
    async for user in users_cursor:
        manager_info = None
        if user.get("Manager"):
            manager = await db["users"].find_one({"_id": ObjectId(user["Manager"])})
            if manager:
                manager_info = {"user_id": str(manager["_id"]), "user_name": manager["Name"]}

        users_list.append({
            "name": user["Name"],
            "role": user["role"],
            "manager": manager_info,
            "email": user["Email"]
        })
    return users_list


@admin_router.post("/admin/change_role/{user_id}")
async def change_role(user_id: str, role: str = Body(..., embed=True), current_user: dict = Depends(get_current_user)):
    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    return {"message": "User role changed successfully"}


@admin_router.post("/admin/change_manager/{user_id}")
async def change_manager(user_id: str, manager_id: str = Body(..., embed=True),
                         current_user: dict = Depends(get_current_user)):
    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"Manager": manager_id}})
    return {"message": "User manager changed successfully"}


@admin_router.post("/admin/send_password/{user_id}")
async def send_password(user_id: str, current_user: dict = Depends(get_current_user)):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hashed_password = get_password_hash(password)
    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"Password_hash": hashed_password}})

    subject = "Your New Expense Tracker Password"
    body = f"Hello {user['Name']},\n\nYour new password is: {password}"
    send_email(subject, body, user["Email"])
    
    return {"message": "User password sent successfully"}


@admin_router.get("/admin/requests")
async def list_all_requests(current_user: dict = Depends(get_current_user)):
    requests_cursor = db["requests"].find({})
    requests_list = []
    async for request in requests_cursor:
        user = await db["users"].find_one({"_id": ObjectId(request["requestor"])})
        requests_list.append({
            "requestor": user["Name"],
            "description": request["description"],
            "request_id": str(request["_id"])
        })
    return requests_list


@admin_router.get("/admin/requests/{request_id}")
async def get_request_details(request_id: str, current_user: dict = Depends(get_current_user)):
    request = await db["requests"].find_one({"_id": ObjectId(request_id)})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    user = await db["users"].find_one({"_id": ObjectId(request["requestor"])})
    request["requestor"] = user["Name"]
    request["request_id"] = str(request["_id"])
    del request["_id"]
    return request


@admin_router.post("/admin/generate_request_rules/{request_id}")
async def generate_request_rules(request_id: str, rule: RequestRule, current_user: dict = Depends(get_current_user)):
    await db["requests"].update_one({"_id": ObjectId(request_id)}, {"$set": rule.dict()})
    # Logic to send to approval process would go here
    return {"message": "Request rules generated and sent for approval"}


@admin_router.get("/admin/expenses")
async def get_all_expenses(current_user: dict = Depends(get_current_user)):
    pending_expense = await db["requests"].count_documents({"status": "submitted"})
    approved_expense = await db["requests"].count_documents({"status": "Approved"})
    return {"Pending_expense": pending_expense, "Approved_expense": approved_expense}


# endregion Admin Routes

# region User Routes
@user_router.post("/user/signin", response_model=Token)
async def user_signin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"Email": form_data.username})
    if not user or not verify_password(form_data.password, user["Password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["Email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/user/change_password")
async def change_password(current_user: dict = Depends(get_current_user), old_password: str = Body(...),
                        new_password: str = Body(...)):
    user = await db["users"].find_one({"Email": current_user["email"]})
    if not verify_password(old_password, user["Password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    hashed_password = get_password_hash(new_password)
    await db["users"].update_one({"Email": current_user["email"]}, {"$set": {"Password_hash": hashed_password}})
    return {"message": "Password changed successfully"}


@user_router.get("/user/requests")
async def get_user_requests(current_user: dict = Depends(get_current_user)):
    user = await db["users"].find_one({"Email": current_user["email"]})
    requests_cursor = db["requests"].find({"requestor": str(user["_id"])})
    requests_list = []
    async for request in requests_cursor:
        requests_list.append({
            "request_id": str(request["_id"]),
            "description": request["description"],
            "status": request["status"]
        })
    return requests_list


@user_router.post("/user/create_request")
async def create_request(request: Request, current_user: dict = Depends(get_current_user)):
    user = await db["users"].find_one({"Email": current_user["email"]})
    request.requestor = str(user["_id"])
    result = await db["requests"].insert_one(request.dict())
    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$push": {"Pending_Requests": str(result.inserted_id)}}
    )
    return {"message": "Request created successfully"}


@user_router.post("/user/approve_request/{request_id}")
async def approve_request(request_id: str, current_user: dict = Depends(get_current_user)):
    # Complex approval logic would be implemented here
    await db["requests"].update_one({"_id": ObjectId(request_id)}, {"$set": {"status": "Approved"}})
    return {"message": "Request approved"}


@user_router.post("/user/reject_request/{request_id}")
async def reject_request(request_id: str, current_user: dict = Depends(get_current_user)):
    # Complex rejection logic would be implemented here
    await db["requests"].update_one({"_id": ObjectId(request_id)}, {"$set": {"status": "Rejected"}})
    return {"message": "Request rejected"}


@user_router.get("/user/team_expense")
async def get_team_expense(current_user: dict = Depends(get_current_user)):
    user = await db["users"].find_one({"Email": current_user["email"]})
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view team expenses")
    
    # Logic to calculate team expenses would go here
    return {"Pending_expense": 0, "Approved_expense": 0}


# endregion User Routes

app.include_router(admin_router, tags=["admin"])
app.include_router(user_router, tags=["user"])

