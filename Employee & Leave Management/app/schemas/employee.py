from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional, Literal
import re


EmploymentType = Literal[
    "Full-Time",
    "Part-Time",
    "Intern",
    "Contract"
]


class EmployeeCreate(BaseModel):
    employee_code: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str

    department_id: int

    designation: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    salary: float = Field(
        ...,
        gt=0
    )

    date_of_joining: date

    employment_type: EmploymentType

    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value > date.today():
            raise ValueError(
                "Date of joining cannot be a future date"
            )

        return value


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50
    )

    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None

    phone: Optional[str] = None

    department_id: Optional[int] = None

    designation: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    salary: Optional[float] = Field(
        None,
        gt=0
    )

    date_of_joining: Optional[date] = None

    employment_type: Optional[EmploymentType] = None

    is_active: Optional[bool] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value

        if not re.fullmatch(r"\d{10}", value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("date_of_joining")
    @classmethod
    def validate_joining_date(cls, value):
        if value is None:
            return value

        if value > date.today():
            raise ValueError(
                "Date of joining cannot be a future date"
            )

        return value


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: EmailStr
    phone: str
    department_id: int
    designation: str
    salary: float
    date_of_joining: date
    employment_type: str
    is_active: bool

    class Config:
        from_attributes = True