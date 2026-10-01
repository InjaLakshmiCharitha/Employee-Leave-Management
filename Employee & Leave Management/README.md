# Employee & Leave Management System
A complete backend REST API built using FastAPI for managing employees, departments, leave requests, authentication, role-based access control, and HR reports.

# Project Objective
The Employee & Leave Management System provides APIs for:
- User registration and login
- JWT authentication
- Role-based access control
- Department management
- Employee management
- Leave management
- Leave approval and rejection
- Leave cancellation
- Leave balance calculation
- Leave validation and business rules
- Dashboard reports
- Leave summary reports
- MySQL database persistence
- Alembic database migrations

# Technologies Used
- Python 3.9+
- FastAPI
- Pydantic
- SQLAlchemy
- MySQL
- PyMySQL
- Alembic
- JWT
- Passlib
- Bcrypt
- Uvicorn
- Python-dotenv
- Swagger UI

# Project Structure
employee_leave_management/
│
├── app/
│   ├── database.py
│   ├── main.py
│   ├── auth/
│   │   ├── dependencies.py
│   │   └── jwt.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── employee.py
│   │   └── leave.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── employee.py
│   │   └── leave.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── departments.py
│   │   ├── employees.py
│   │   ├── leaves.py
│   │   └── reports.py
│   └── services/
│       └── leave_service.py
│
├── alembic/
│   ├── versions/
│   │   └── migration_file.py
│   ├── env.py
│   ├── script.py.mako
│   └── README
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md

# Features
# Authentication
The system supports three user roles:
- Admin
- HR
- Employee
Authentication is implemented using JWT tokens.

# Authentication APIs
* POST /auth/register
* POST /auth/login
* GET  /auth/me

# JWT Features
- Secure password hashing
- JWT access tokens
- Token expiration
- Invalid token protection
- Expired token protection
- Inactive user protection
JWT token expiration is configured for 30 minutes.

# Role-Based Access Control
# Admin
Admin can:
- Manage departments
- Manage employees
- View employees
- Manage leaves
- Approve leaves
- Reject leaves
- Cancel leaves
- View reports
- Access the complete system

# HR
HR can:
- Create employees
- Update employees
- View employees
- Manage leave requests
- Approve leaves
- Reject leaves
- View reports

# Employee
Employee can:
- View their own employee details
- Apply for their own leave
- View their own leaves
- View their leave balance
- Cancel their pending leave
Employees cannot access other employees' private information.

# Department Management
Department APIs:
* POST   /departments
* GET    /departments
* GET    /departments/{department_id}
* PUT    /departments/{department_id}
* DELETE /departments/{department_id}
* GET    /departments/{department_id}/employees

Department fields:
- id
- department_name
- location
- is_active
- created_at
- updated_at
- Department names are unique.
- A department containing active employees cannot be deleted.

# Employee Management
Employee APIs:
* POST   /employees
* GET    /employees
* GET    /employees/{employee_id}
* PUT    /employees/{employee_id}
* DELETE /employees/{employee_id}
* GET    /employees/{employee_id}/leaves
* GET    /employees/{employee_id}/leave-balance

Employee fields:
- id
- employee_code
- name
- email
- phone
- department_id
- designation
- salary
- date_of_joining
- employment_type
- is_active
- created_at
- updated_at

Supported employment types:
- Full-Time
- Part-Time
- Intern
- Contract

Employee code and email must be unique.

Deleting an employee performs a soft delete by setting:
- is_active = false


# Employee Search, Filtering and Sorting
The employee API supports searching, filtering, sorting and pagination.
- Search by Name
- Filter by Department
- Filter by Designation
- Filter by Employment Type
- Filter by Active Status
- Sort by Salary
- Pagination

# Leave Management
Leave APIs:
* POST /leaves
* GET  /leaves
* GET  /leaves/{leave_id}
* PUT  /leaves/{leave_id}/approve
* PUT  /leaves/{leave_id}/reject
* PUT  /leaves/{leave_id}/cancel

Supported leave types:
- Sick
- Casual
- Earned

Supported leave status:
- Pending
- Approved
- Rejected
- Cancelled

# Leave Balance
Annual leave limits:
| Leave Type | Annual Limit |
|------------|--------------|
| Sick   | 12 days |
| Casual | 10 days |
| Earned | 15 days |

Leave balance is reduced only after the leave is approved.

# Leave Business Rules
The system validates:
- Employees can apply only for themselves
- Inactive employees cannot apply for leave
- Leave cannot start in the past
- End date cannot be before start date
- Weekends are excluded from total leave days
- Insufficient leave balance prevents application
- Overlapping leaves are prevented
- Only Pending leaves can be approved
- Only Pending leaves can be rejected
- Only Pending leaves can be cancelled
- Rejection reason is required
- HR cannot approve their own leave
- Leave balance is deducted only after approval

# Leave Search and Filtering
Leave requests can be filtered using:
- status
- leave_type
- employee_id
- start_date
- end_date
- Pagination is supported:
GET /leaves?skip=0&limit=10

# Reports
The system provides reports for Admin and HR users.

# Dashboard Report
The dashboard provides:
- Total employees
- Active employees
- Inactive employees
- Total departments
- Active departments
- Total leaves
- Pending leaves
- Approved leaves
- Rejected leaves
- Cancelled leaves
Only Admin and HR users can access reports.

# Leave Summary Report
The report provides:
- Sick leave days
- Casual leave days
- Earned leave days
- Pending requests
- Approved requests
- Rejected requests
- Cancelled requests

# Database
The project uses MySQL.

Database name:
employee_leave_management_db

Main tables:
users
departments
employees
leave_requests
alembic_version

# Database Relationships

Department
    |
    └── Employees
          |
          └── Leave Requests

# Environment Variables
Create a '.env' file in the project root.

DATABASE_URL=mysql+pymysql://root:MYSQL_PASSWORD@localhost:3306/employee_leave_management_db

JWT_SECRET_KEY=my-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30


# Installation
# Create Virtual Environment
- python -m venv venv
Activate the virtual environment:
- venv\Scripts\activate

# Install Packages
- pip install fastapi uvicorn sqlalchemy pymysql alembic python-dotenv python-jose[cryptography] passlib[bcrypt] pydantic[email]

# Create MySQL Database
- CREATE DATABASE employee_leave_management_db;

# Run Alembic Migration
- alembic upgrade head
This creates the required database tables.
The project uses Alembic for database migrations instead of SQLAlchemy 'create_all()'.

# Start FastAPI Server
- uvicorn app.main:app --reload

- The application will run at:
  http://127.0.0.1:8000


# Swagger Documentation

Open:
http://127.0.0.1:8000/docs

Swagger UI can be used to:
- Register users
- Login
- Authorize JWT
- Create departments
- Create employees
- Apply leaves
- Approve leaves
- Reject leaves
- Cancel leaves
- View leave balances
- View reports
- Test validations

# API Testing Flow
Recommended testing order:
1. Register Admin
        ↓
2. Login Admin
        ↓
3. Authorize JWT
        ↓
4. Create Departments
        ↓
5. Create Employees
        ↓
6. Register/Login Employees
        ↓
7. Apply Leave
        ↓
8. Approve/Reject Leave
        ↓
9. Check Leave Balance
        ↓
10. Test Validation Errors
        ↓
11. Test Reports


# HTTP Status Codes
| Status Code | Meaning |
|-------------|---------|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Bad request or business rule violation |
| 401 | Unauthorized or invalid token |
| 403 | Forbidden or insufficient permissions |
| 404 | Resource not found |
| 409 | Duplicate or conflict |
| 422 | Validation error |

# Security
The project follows these security practices:
- Passwords are hashed before storage
- JWT authentication is used
- JWT tokens expire
- '.env' is excluded from Git
- Database credentials are not stored directly in source code
- Role-based authorization is implemented
- Inactive users cannot login
- Employees cannot access other employee profiles

# Project Testing
The project was tested using Swagger UI.
Testing includes:
- User registration
- User login
- JWT authorization
- Role-based access control
- Department CRUD
- Employee CRUD
- Employee search
- Employee filtering
- Employee sorting
- Pagination
- Leave application
- Leave approval
- Leave rejection
- Leave cancellation
- Leave balance
- Weekend calculation
- Leave overlap validation
- Duplicate validation
- Date validation
- Phone validation
- Salary validation
- Unauthorized access
- Forbidden access
- Dashboard reports
- Leave summary reports

# Conclusion
The Employee & Leave Management System is a FastAPI-based backend application that provides employee, department and leave management functionality with authentication, authorization, validations, business rules, reporting, MySQL persistence and Alembic database migrations.
The API is documented and testable through Swagger UI.