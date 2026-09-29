from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    def register_user(self, db: Session, user_in: UserRegister) -> User:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered."
            )
        
        user = User(
            name=user_in.name,
            email=user_in.email.lower(),
            password_hash=get_password_hash(user_in.password),
            role=user_in.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, login_in: UserLogin) -> tuple[User, str]:
        user = db.query(User).filter(User.email == login_in.email.lower()).first()
        if not user or not verify_password(login_in.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = create_access_token(subject=user.id)
        return user, token

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()


auth_service = AuthService()
