from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.models.user import User
from app.models.leave import LeaveRequest


from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse
)

from app.schemas.leave import LeaveResponse
from app.schemas.leave import LeaveBalanceResponse
from app.services.leave_service import get_leave_balance

from app.auth.dependencies import (
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


# CREATE EMPLOYEE
# Admin and HR

@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    # Check employee code
    existing_code = db.query(Employee).filter(
        Employee.employee_code ==
        employee_data.employee_code
    ).first()

    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee code already exists"
        )

    # Check email
    existing_email = db.query(Employee).filter(
        Employee.email == employee_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists"
        )

    # Check department
    department = db.query(Department).filter(
        Department.id == employee_data.department_id,
        Department.is_active == True
    ).first()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active department not found"
        )

    employee = Employee(
        employee_code=employee_data.employee_code,
        name=employee_data.name,
        email=employee_data.email,
        phone=employee_data.phone,
        department_id=employee_data.department_id,
        designation=employee_data.designation,
        salary=employee_data.salary,
        date_of_joining=employee_data.date_of_joining,
        employment_type=employee_data.employment_type,
        is_active=employee_data.is_active
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


# GET ALL EMPLOYEES
# Search + Filter + Pagination + Sorting

@router.get(
    "",
    response_model=list[EmployeeResponse]
)
def get_employees(
    name: str | None = None,
    department_id: int | None = None,
    designation: str | None = None,
    employment_type: str | None = None,
    is_active: bool | None = None,

    sort_by: str = "id",
    order: str = "asc",

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

    query = db.query(Employee)

    # Search by name
    if name:
        query = query.filter(
            Employee.name.ilike(f"%{name}%")
        )

    # Department filter
    if department_id is not None:
        query = query.filter(
            Employee.department_id == department_id
        )

    # Designation filter
    if designation:
        query = query.filter(
            Employee.designation.ilike(
                f"%{designation}%"
            )
        )

    # Employment type filter
    if employment_type:
        allowed_types = [
            "Full-Time",
            "Part-Time",
            "Intern",
            "Contract"
        ]

        if employment_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid employment type"
            )

        query = query.filter(
            Employee.employment_type ==
            employment_type
        )

    # Active filter
    if is_active is not None:
        query = query.filter(
            Employee.is_active == is_active
        )

    # Sorting
    sort_columns = {
        "id": Employee.id,
        "name": Employee.name,
        "salary": Employee.salary,
        "date_of_joining": Employee.date_of_joining
    }

    if sort_by not in sort_columns:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. Use id, name, "
                "salary, or date_of_joining"
            )
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="order must be asc or desc"
        )

    sort_column = sort_columns[sort_by]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    employees = query.offset(
        skip
    ).limit(
        limit
    ).all()

    return employees


# GET EMPLOYEE BY ID

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Employee can only see their own details.
    # Admin and HR can see everyone.
    if current_user.role == "Employee":

        if current_user.email != employee.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own details"
            )

    return employee


# UPDATE EMPLOYEE
# Admin and HR

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    if employee_data.employee_code is not None:

        existing_code = db.query(Employee).filter(
            Employee.employee_code ==
            employee_data.employee_code,
            Employee.id != employee_id
        ).first()

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee code already exists"
            )

        employee.employee_code = (
            employee_data.employee_code
        )

    if employee_data.email is not None:

        existing_email = db.query(Employee).filter(
            Employee.email == employee_data.email,
            Employee.id != employee_id
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee email already exists"
            )

        employee.email = employee_data.email

    if employee_data.name is not None:
        employee.name = employee_data.name

    if employee_data.phone is not None:
        employee.phone = employee_data.phone

    if employee_data.department_id is not None:

        department = db.query(Department).filter(
            Department.id ==
            employee_data.department_id,
            Department.is_active == True
        ).first()

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active department not found"
            )

        employee.department_id = (
            employee_data.department_id
        )

    if employee_data.designation is not None:
        employee.designation = (
            employee_data.designation
        )

    if employee_data.salary is not None:
        employee.salary = employee_data.salary

    if employee_data.date_of_joining is not None:
        employee.date_of_joining = (
            employee_data.date_of_joining
        )

    if employee_data.employment_type is not None:
        employee.employment_type = (
            employee_data.employment_type
        )

    if employee_data.is_active is not None:
        employee.is_active = (
            employee_data.is_active
        )

    db.commit()
    db.refresh(employee)

    return employee


# SOFT DELETE EMPLOYEE
# Admin and HR

@router.delete(
    "/{employee_id}"
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "HR")
    )
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    employee.is_active = False

    db.commit()

    return {
        "message": "Employee deactivated successfully"
    }


# GET EMPLOYEE LEAVES

@router.get(
    "/{employee_id}/leaves",
    response_model=list[LeaveResponse]
)
def get_employee_leaves(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Employee can see only own leaves
    if current_user.role == "Employee":

        if employee.email != current_user.email:

            raise HTTPException(
                status_code=403,
                detail="You can view only your own leaves"
            )

    return (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id
        )
        .order_by(LeaveRequest.id.desc())
        .all()
    )


# GET EMPLOYEE LEAVE BALANCE

@router.get(
    "/{employee_id}/leave-balance",
    response_model=LeaveBalanceResponse
)
def get_employee_leave_balance(
    employee_id: int,
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Employee can see only own balance
    if current_user.role == "Employee":

        if employee.email != current_user.email:

            raise HTTPException(
                status_code=403,
                detail="You can view only your own leave balance"
            )

    if year is None:
        year = date.today().year

    balance = get_leave_balance(
        db,
        employee_id,
        year
    )

    return {
        "employee_id": employee_id,
        "year": year,

        "sick_total": balance["Sick"]["total"],
        "sick_used": balance["Sick"]["used"],
        "sick_remaining": balance["Sick"]["remaining"],

        "casual_total": balance["Casual"]["total"],
        "casual_used": balance["Casual"]["used"],
        "casual_remaining": balance["Casual"]["remaining"],

        "earned_total": balance["Earned"]["total"],
        "earned_used": balance["Earned"]["used"],
        "earned_remaining": balance["Earned"]["remaining"]
    }