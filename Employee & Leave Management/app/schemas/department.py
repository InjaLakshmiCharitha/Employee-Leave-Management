from pydantic import BaseModel, Field
from typing import Optional


class DepartmentCreate(BaseModel):
    department_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    location: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    is_active: bool = True


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    location: Optional[str] = Field(
        None,
        min_length=2,
        max_length=150
    )

    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    location: str
    is_active: bool

    class Config:
        from_attributes = True