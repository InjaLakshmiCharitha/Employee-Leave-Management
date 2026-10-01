from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, Literal


LeaveType = Literal["Sick", "Casual", "Earned"]

LeaveStatus = Literal[
    "Pending",
    "Approved",
    "Rejected",
    "Cancelled"
]


# Apply Leave

class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=3, max_length=500)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value, info):
        start_date = info.data.get("start_date")

        if start_date and value < start_date:
            raise ValueError(
                "End date cannot be before start date"
            )

        return value


# Leave Response

class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    total_days: int
    reason: str
    status: str
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True


# Reject Leave

class LeaveReject(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=3,
        max_length=500
    )


# Leave Balance

class LeaveBalanceResponse(BaseModel):
    employee_id: int
    year: int

    sick_total: int
    sick_used: int
    sick_remaining: int

    casual_total: int
    casual_used: int
    casual_remaining: int

    earned_total: int
    earned_used: int
    earned_remaining: int