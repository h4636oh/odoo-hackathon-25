import motor.motor_asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from bson import ObjectId

class DatabaseManager:
    def __init__(self, database: motor.motor_asyncio.AsyncIOMotorDatabase):
        self.db = database
        self.users = database.users
        self.companies = database.companies
        self.requests = database.requests
        self.rules = database.rules

    async def create_user(self, user_data: dict) -> dict:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user_data.update({
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await self.users.insert_one(user_data)
        return await self.users.find_one({"_id": result.inserted_id})

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        return await self.users.find_one({"email": email})

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        return await self.users.find_one({"user_id": user_id})

    async def update_user(self, user_id: str, update_data: dict) -> Optional[dict]:
        """Update user data."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_user_by_id(user_id)
        return None

    async def get_all_users(self, company_id: str) -> List[dict]:
        """Get all users for a company."""
        cursor = self.users.find({"company_id": company_id})
        users = []
        async for user in cursor:
            # Get manager info if exists
            if user.get("manager_id"):
                manager = await self.get_user_by_id(user["manager_id"])
                if manager:
                    user["manager"] = {
                        "user_id": manager["user_id"],
                        "name": manager["name"]
                    }
            users.append(user)
        return users

    async def create_company(self, company_data: dict) -> dict:
        """Create a new company."""
        company_id = str(uuid.uuid4())
        company_data.update({
            "company_id": company_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await self.companies.insert_one(company_data)
        return await self.companies.find_one({"_id": result.inserted_id})

    async def get_company_by_email(self, email: str) -> Optional[dict]:
        """Get company by admin email."""
        return await self.companies.find_one({"admin_email": email})

    async def get_company_by_id(self, company_id: str) -> Optional[dict]:
        """Get company by ID."""
        return await self.companies.find_one({"company_id": company_id})

    async def create_request(self, request_data: dict) -> dict:
        """Create a new request."""
        request_id = str(uuid.uuid4())
        request_data.update({
            "request_id": request_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await self.requests.insert_one(request_data)
        return await self.requests.find_one({"_id": result.inserted_id})

    async def get_request_by_id(self, request_id: str) -> Optional[dict]:
        """Get request by ID."""
        return await self.requests.find_one({"request_id": request_id})

    async def get_requests_by_user(self, user_id: str) -> List[dict]:
        """Get all requests for a user."""
        cursor = self.requests.find({"requestor": user_id})
        requests = []
        async for request in cursor:
            requests.append(request)
        return requests

    async def get_all_requests(self, company_id: str) -> List[dict]:
        """Get all requests for a company."""
        cursor = self.requests.find({"company_id": company_id})
        requests = []
        async for request in cursor:
            requests.append(request)
        return requests

    async def update_request(self, request_id: str, update_data: dict) -> Optional[dict]:
        """Update request data."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.requests.update_one(
            {"request_id": request_id},
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_request_by_id(request_id)
        return None

    async def create_rule(self, rule_data: dict) -> dict:
        """Create a new approval rule."""
        rule_id = str(uuid.uuid4())
        rule_data.update({
            "rule_id": rule_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await self.rules.insert_one(rule_data)
        return await self.rules.find_one({"_id": result.inserted_id})

    async def get_rule_by_request_id(self, request_id: str) -> Optional[dict]:
        """Get rule by request ID."""
        return await self.rules.find_one({"request_id": request_id})

    async def get_expense_summary(self, company_id: str) -> dict:
        """Get expense summary for a company."""
        pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": "$status",
                "total_amount": {"$sum": "$payment_Amount"}
            }}
        ]
        
        cursor = self.requests.aggregate(pipeline)
        summary = {"Pending_expense": 0, "Approved_expense": 0}
        
        async for result in cursor:
            status = result["_id"].lower()
            if status == "pending":
                summary["Pending_expense"] = result["total_amount"]
            elif status == "approved":
                summary["Approved_expense"] = result["total_amount"]
        
        return summary

    async def get_team_expense_summary(self, manager_id: str) -> dict:
        """Get team expense summary for a manager."""
        # Get all users managed by this manager
        managed_users = []
        cursor = self.users.find({"manager_id": manager_id})
        async for user in cursor:
            managed_users.append(user["user_id"])
        
        if not managed_users:
            return {"Pending_expense": 0, "Approved_expense": 0}
        
        # Get expenses for managed users
        pipeline = [
            {"$match": {"requestor": {"$in": managed_users}}},
            {"$group": {
                "_id": "$status",
                "total_amount": {"$sum": "$payment_Amount"}
            }}
        ]
        
        cursor = self.requests.aggregate(pipeline)
        summary = {"Pending_expense": 0, "Approved_expense": 0}
        
        async for result in cursor:
            status = result["_id"].lower()
            if status == "pending":
                summary["Pending_expense"] = result["total_amount"]
            elif status == "approved":
                summary["Approved_expense"] = result["total_amount"]
        
        return summary
