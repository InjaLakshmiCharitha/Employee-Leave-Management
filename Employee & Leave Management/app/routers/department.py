from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import Department
from app.models.employee import Employee

from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)

from app.auth.dependencies import (
    get_current_user,
    require_roles
)

from app.models.user import User


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


# CREATE DEPARTMENT
# Admin only

@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin")
    )
):

    existing_department = db.query(Department).filter(
        Department.department_name ==
        department_data.department_name
    ).first()

    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department name already exists"
        )

    department = Department(
        department_name=department_data.department_name,
        location=department_data.location,
        is_active=department_data.is_active
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


# GET ALL DEPARTMENTS

@router.get(
    "",
    response_model=list[DepartmentResponse]
)
def get_departments(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="skip cannot be negative"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100"
        )

    departments = db.query(Department).offset(
        skip
    ).limit(
        limit
    ).all()

    return departments


# GET DEPARTMENT BY ID

@router.get(
    "/{department_id}",
    response_model=DepartmentResponse
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return department


# UPDATE DEPARTMENT
# Admin only

@router.put(
    "/{department_id}",
    response_model=DepartmentResponse
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin")
    )
):

    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    if department_data.department_name:

        existing_department = db.query(
            Department
        ).filter(
            Department.department_name ==
            department_data.department_name,
            Department.id != department_id
        ).first()

        if existing_department:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists"
            )

        department.department_name = (
            department_data.department_name
        )

    if department_data.location is not None:
        department.location = department_data.location

    if department_data.is_active is not None:
        department.is_active = department_data.is_active

    db.commit()
    db.refresh(department)

    return department


# DELETE DEPARTMENT
# Admin only

@router.delete(
    "/{department_id}"
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin")
    )
):

    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    active_employee = db.query(Employee).filter(
        Employee.department_id == department_id,
        Employee.is_active == True
    ).first()

    if active_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Department cannot be deleted because "
                "it has active employees"
            )
        )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }


# GET EMPLOYEES IN DEPARTMENT

@router.get(
    "/{department_id}/employees"
)
def get_department_employees(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    employees = db.query(Employee).filter(
        Employee.department_id == department_id,
        Employee.is_active == True
    ).all()

    return employees