from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.user import User

from app.schemas.leave import (
    LeaveCreate,
    LeaveResponse,
    LeaveReject,
    LeaveBalanceResponse
)

from app.auth.dependencies import (
    get_current_user,
    require_roles
)

from app.services.leave_service import (
    LEAVE_LIMITS,
    get_employee_for_user,
    calculate_working_days,
    get_leave_balance,
    check_leave_overlap
)


router = APIRouter(
    prefix="/leaves",
    tags=["Leaves"]
)


# APPLY LEAVE

@router.post(
    "",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_leave(
    leave_data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find employee belonging to logged-in user
    employee = get_employee_for_user(
        db,
        current_user
    )

    # Employees can apply only for themselves
    if leave_data.employee_id != employee.id:

        raise HTTPException(
            status_code=403,
            detail="You can apply leave only for yourself"
        )

    # Inactive employees cannot apply
    if not employee.is_active:

        raise HTTPException(
            status_code=400,
            detail="Inactive employees cannot apply for leave"
        )

    # Start date cannot be in the past
    if leave_data.start_date < date.today():

        raise HTTPException(
            status_code=400,
            detail="Leave cannot start in the past"
        )

    # End date cannot be before start date
    if leave_data.end_date < leave_data.start_date:

        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # Calculate working days
    total_days = calculate_working_days(
        leave_data.start_date,
        leave_data.end_date
    )

    # If only weekend dates are selected
    if total_days == 0:

        raise HTTPException(
            status_code=400,
            detail="Leave must contain at least one working day"
        )

    # Check overlapping leave
    overlapping_leave = check_leave_overlap(
        db,
        employee.id,
        leave_data.start_date,
        leave_data.end_date
    )

    if overlapping_leave:

        raise HTTPException(
            status_code=409,
            detail="Leave dates overlap with an existing leave request"
        )

    # Check leave balance
    year = leave_data.start_date.year

    balance = get_leave_balance(
        db,
        employee.id,
        year
    )

    remaining = balance[leave_data.leave_type]["remaining"]

    if total_days > remaining:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Insufficient {leave_data.leave_type} leave balance. "
                f"Remaining balance: {remaining} days"
            )
        )

    # Create leave
    new_leave = LeaveRequest(
        employee_id=employee.id,
        leave_type=leave_data.leave_type,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        total_days=total_days,
        reason=leave_data.reason,
        status="Pending"
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave


# GET ALL LEAVES

@router.get(
    "",
    response_model=list[LeaveResponse]
)
def get_leaves(
    status_filter: str | None = Query(None, alias="status"),
    leave_type: str | None = None,
    employee_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,

    skip: int = 0,
    limit: int = 10,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip cannot be negative"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    query = db.query(LeaveRequest)

    # Employee can see only own leaves
    if current_user.role == "Employee":

        employee = get_employee_for_user(
            db,
            current_user
        )

        query = query.filter(
            LeaveRequest.employee_id == employee.id
        )

    else:

        # Admin / HR can filter by employee
        if employee_id is not None:
            query = query.filter(
                LeaveRequest.employee_id == employee_id
            )

    # Status filter
    if status_filter:

        allowed_statuses = [
            "Pending",
            "Approved",
            "Rejected",
            "Cancelled"
        ]

        if status_filter not in allowed_statuses:

            raise HTTPException(
                status_code=400,
                detail="Invalid leave status"
            )

        query = query.filter(
            LeaveRequest.status == status_filter
        )

    # Leave type filter
    if leave_type:

        if leave_type not in LEAVE_LIMITS:

            raise HTTPException(
                status_code=400,
                detail="Invalid leave type"
            )

        query = query.filter(
            LeaveRequest.leave_type == leave_type
        )

    # Date filters
    if start_date:

        query = query.filter(
            LeaveRequest.start_date >= start_date
        )

    if end_date:

        query = query.filter(
            LeaveRequest.end_date <= end_date
        )

    return (
        query
        .order_by(LeaveRequest.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# GET LEAVE BY ID

@router.get(
    "/{leave_id}",
    response_model=LeaveResponse
)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:

        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Employee can see only own leave
    if current_user.role == "Employee":

        employee = get_employee_for_user(
            db,
            current_user
        )

        if leave.employee_id != employee.id:

            raise HTTPException(
                status_code=403,
                detail="You can view only your own leave requests"
            )

    return leave


# APPROVE LEAVE

@router.put(
    "/{leave_id}/approve",
    response_model=LeaveResponse
)
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:

        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Only pending leaves can be approved
    if leave.status != "Pending":

        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be approved"
        )

    employee = (
        db.query(Employee)
        .filter(Employee.id == leave.employee_id)
        .first()
    )

    if not employee:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # HR cannot approve their own leave
    if (
        current_user.role == "HR"
        and employee.email == current_user.email
    ):

        raise HTTPException(
            status_code=403,
            detail="HR cannot approve their own leave"
        )

    # Check balance again before approval
    year = leave.start_date.year

    balance = get_leave_balance(
        db,
        employee.id,
        year
    )

    remaining = balance[leave.leave_type]["remaining"]

    if leave.total_days > remaining:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Insufficient {leave.leave_type} balance "
                f"for approval. Remaining: {remaining}"
            )
        )

    # Approve
    leave.status = "Approved"
    leave.approved_by = current_user.id

    db.commit()
    db.refresh(leave)

    return leave


# REJECT LEAVE

@router.put(
    "/{leave_id}/reject",
    response_model=LeaveResponse
)
def reject_leave(
    leave_id: int,
    rejection_data: LeaveReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:

        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Only pending leaves can be rejected
    if leave.status != "Pending":

        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be rejected"
        )

    leave.status = "Rejected"

    leave.rejection_reason = (
        rejection_data.rejection_reason
    )

    db.commit()
    db.refresh(leave)

    return leave


# CANCEL LEAVE

@router.put(
    "/{leave_id}/cancel",
    response_model=LeaveResponse
)
def cancel_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    leave = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == leave_id)
        .first()
    )

    if not leave:

        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    # Only pending leaves can be cancelled
    if leave.status != "Pending":

        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be cancelled"
        )

    # Employee can cancel only own leave
    if current_user.role == "Employee":

        employee = get_employee_for_user(
            db,
            current_user
        )

        if leave.employee_id != employee.id:

            raise HTTPException(
                status_code=403,
                detail="You can cancel only your own leave"
            )

    leave.status = "Cancelled"

    db.commit()
    db.refresh(leave)

    return leave