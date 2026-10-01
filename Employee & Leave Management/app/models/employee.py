from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    Numeric,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String(10),
        nullable=False
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False
    )

    designation = Column(
        String(100),
        nullable=False
    )

    salary = Column(
        Numeric(10, 2),
        nullable=False
    )

    date_of_joining = Column(
        Date,
        nullable=False
    )

    employment_type = Column(
        String(20),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
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

    department = relationship(
        "Department",
        back_populates="employees"
    )

    leave_requests = relationship(
        "LeaveRequest",
        back_populates="employee"
    )