from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import departments, staffs, overtime, info
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weekend Overtime Management API",
    description="API for managing weekend overtime schedules",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
app.include_router(staffs.router, prefix="/api/staffs", tags=["staffs"])
app.include_router(overtime.router, prefix="/api/overtime", tags=["overtime"])
app.include_router(info.router, prefix="/api/info", tags=["info"])

# Serve static files (for production)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Weekend Overtime Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
