from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    leave_type = Column(
        String(20),
        nullable=False
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    total_days = Column(
        Integer,
        nullable=False
    )

    reason = Column(
        String(500),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="Pending"
    )

    approved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    rejection_reason = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    employee = relationship(
        "Employee",
        back_populates="leave_requests"
    )