from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.department import router as department_router
from app.routers.employee import router as employee_router
from app.routers.leave import router as leave_router
from app.routers.reports import router as report_router

app = FastAPI(
    title="Employee & Leave Management System",
    description="Backend API for Employee, Department and Leave Management",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(department_router)
app.include_router(employee_router)
app.include_router(leave_router)
app.include_router(report_router)

@app.get("/")
def home():
    return {
        "message": "Employee & Leave Management System API is running"
    } 