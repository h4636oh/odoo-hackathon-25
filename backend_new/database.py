import motor.motor_asyncio
from config import MONGODB_URL, DATABASE_NAME

# Initialize MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.users
companies_collection = database.companies
requests_collection = database.requests
rules_collection = database.rules
