from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.leave import LeaveRequest

from app.auth.dependencies import require_roles


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# DASHBOARD REPORT

@router.get("/dashboard")
def dashboard_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    # Employee counts

    total_employees = (
        db.query(Employee)
        .count()
    )

    active_employees = (
        db.query(Employee)
        .filter(Employee.is_active == True)
        .count()
    )

    inactive_employees = (
        db.query(Employee)
        .filter(Employee.is_active == False)
        .count()
    )


    # Department count

    total_departments = (
        db.query(Department)
        .count()
    )

    active_departments = (
        db.query(Department)
        .filter(Department.is_active == True)
        .count()
    )


    # Leave counts

    total_leaves = (
        db.query(LeaveRequest)
        .count()
    )

    pending_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Pending"
        )
        .count()
    )

    approved_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Approved"
        )
        .count()
    )

    rejected_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Rejected"
        )
        .count()
    )

    cancelled_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Cancelled"
        )
        .count()
    )


    return {
        "employees": {
            "total": total_employees,
            "active": active_employees,
            "inactive": inactive_employees
        },

        "departments": {
            "total": total_departments,
            "active": active_departments
        },

        "leaves": {
            "total": total_leaves,
            "pending": pending_leaves,
            "approved": approved_leaves,
            "rejected": rejected_leaves,
            "cancelled": cancelled_leaves
        }
    }


# LEAVE SUMMARY REPORT

@router.get("/leave-summary")
def leave_summary_report(
    year: int | None = Query(
        default=None,
        description="Year for the report"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    if year is None:
        from datetime import date
        year = date.today().year


    # Total leave days by type

    sick_days = (
        db.query(
            func.coalesce(
                func.sum(LeaveRequest.total_days),
                0
            )
        )
        .filter(
            LeaveRequest.leave_type == "Sick",
            LeaveRequest.status == "Approved",
            func.year(LeaveRequest.start_date) == year
        )
        .scalar()
    )


    casual_days = (
        db.query(
            func.coalesce(
                func.sum(LeaveRequest.total_days),
                0
            )
        )
        .filter(
            LeaveRequest.leave_type == "Casual",
            LeaveRequest.status == "Approved",
            func.year(LeaveRequest.start_date) == year
        )
        .scalar()
    )


    earned_days = (
        db.query(
            func.coalesce(
                func.sum(LeaveRequest.total_days),
                0
            )
        )
        .filter(
            LeaveRequest.leave_type == "Earned",
            LeaveRequest.status == "Approved",
            func.year(LeaveRequest.start_date) == year
        )
        .scalar()
    )


    # Leave request counts

    pending = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Pending",
            func.year(LeaveRequest.start_date) == year
        )
        .count()
    )

    approved = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Approved",
            func.year(LeaveRequest.start_date) == year
        )
        .count()
    )

    rejected = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Rejected",
            func.year(LeaveRequest.start_date) == year
        )
        .count()
    )

    cancelled = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Cancelled",
            func.year(LeaveRequest.start_date) == year
        )
        .count()
    )


    return {
        "year": year,

        "leave_days": {
            "Sick": sick_days,
            "Casual": casual_days,
            "Earned": earned_days
        },

        "requests": {
            "Pending": pending,
            "Approved": approved,
            "Rejected": rejected,
            "Cancelled": cancelled
        }
    }