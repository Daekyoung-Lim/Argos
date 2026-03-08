from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .service import verify_password, create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    employee_no: str
    password: str


class DepartmentInfo(BaseModel):
    dept_id: int
    dept_name: str


class UserInfo(BaseModel):
    user_id: int
    employee_no: str
    name: str
    email: str
    role: str
    department: DepartmentInfo | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_no == request.employee_no).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token_data = {
        "user_id": user.user_id,
        "employee_no": user.employee_no,
        "role": user.role,
    }
    access_token = create_access_token(data=token_data)

    dept_info = None
    if user.department:
        dept_info = DepartmentInfo(
            dept_id=user.department.dept_id,
            dept_name=user.department.dept_name,
        )

    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            user_id=user.user_id,
            employee_no=user.employee_no,
            name=user.name,
            email=user.email,
            role=user.role,
            department=dept_info,
        ),
    )
