from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.user import User


# Leave limits per year
LEAVE_LIMITS = {
    "Sick": 12,
    "Casual": 10,
    "Earned": 15
}


# Find employee belonging to logged-in user

def get_employee_for_user(db: Session, user: User):

    employee = (
        db.query(Employee)
        .filter(Employee.email == user.email)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee profile not found for this user"
        )

    return employee


# Calculate working days
# Excludes Saturday and Sunday

def calculate_working_days(start_date: date, end_date: date):

    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    total_days = 0
    current_date = start_date

    while current_date <= end_date:

        # Monday = 0
        # Saturday = 5
        # Sunday = 6

        if current_date.weekday() < 5:
            total_days += 1

        current_date += timedelta(days=1)

    return total_days


# Get approved leave days

def get_used_leave_days(
    db: Session,
    employee_id: int,
    leave_type: str,
    year: int
):

    leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == leave_type,
            LeaveRequest.status == "Approved",
            LeaveRequest.start_date >= date(year, 1, 1),
            LeaveRequest.start_date <= date(year, 12, 31)
        )
        .all()
    )

    used_days = sum(leave.total_days for leave in leaves)

    return used_days


# Get remaining leave balance

def get_leave_balance(
    db: Session,
    employee_id: int,
    year: int
):

    balance = {}

    for leave_type, limit in LEAVE_LIMITS.items():

        used = get_used_leave_days(
            db,
            employee_id,
            leave_type,
            year
        )

        remaining = max(limit - used, 0)

        balance[leave_type] = {
            "total": limit,
            "used": used,
            "remaining": remaining
        }

    return balance


# Check overlapping leave

def check_leave_overlap(
    db: Session,
    employee_id: int,
    start_date: date,
    end_date: date
):

    overlapping_leave = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,

            # Ignore rejected/cancelled leaves
            LeaveRequest.status.notin_(
                ["Rejected", "Cancelled"]
            ),

            # Date overlap condition
            LeaveRequest.start_date <= end_date,
            LeaveRequest.end_date >= start_date
        )
        .first()
    )

    return overlapping_leave