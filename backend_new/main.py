from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import motor.motor_asyncio
from pymongo import MongoClient
import os
from database import database, users_collection, companies_collection, requests_collection, rules_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    # Create indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("user_id", unique=True)
    await companies_collection.create_index("company_name", unique=True)
    await requests_collection.create_index("request_id", unique=True)
    yield
    # Shutdown
    print("Shutting down...")
    client.close()

# Initialize FastAPI app
app = FastAPI(
    title="Expense Management API",
    description="API for managing expense requests and approvals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)

# Security
security = HTTPBearer()

# Import routers
from routers import auth, admin, user

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(user.router, prefix="/user", tags=["User"])

@app.get("/")
async def root():
    return {"message": "Expense Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
