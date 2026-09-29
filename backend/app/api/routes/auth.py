from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import auth_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, user_in)
    return user


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user, token = auth_service.authenticate_user(db, login_in)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
