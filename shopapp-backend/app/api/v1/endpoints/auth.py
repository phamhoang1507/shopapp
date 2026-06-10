from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, get_current_user
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await UserService.get_by_email(db, data.email)
    if existing:
        raise HTTPException(400, "Email đã được đăng ký")

    user = await UserService.create(db, data)
    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await UserService.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(401, "Email hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(403, "Tài khoản bị khóa")

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Token không hợp lệ")

    user = await UserService.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(401, "Tài khoản không tồn tại")

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user
