#!/usr/bin/env python3

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all backend modules can be imported"""
    try:
        from app.database import get_db, Base
        print("✅ Database module imported")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from app.models import Department, Staff, SubDepartment, Sat, Sun
        print("✅ Models imported")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from app.routers import departments, staffs, overtime, info
        print("✅ Routers imported")
    except Exception as e:
        print(f"❌ Routers import failed: {e}")
        return False
    
    try:
        from app.main import app
        print("✅ FastAPI app imported")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastAPI Backend...")
    print("=" * 40)
    
    imports_ok = test_imports()
    
    if imports_ok:
        print("\nTesting database connection...")
        test_database_connection()
    
    print("\n" + "=" * 40)
    if imports_ok:
        print("✅ Backend structure is ready!")
        print("Install dependencies with: cd backend && pip install -r requirements.txt")
    else:
        print("❌ Backend has import issues that need fixing")
