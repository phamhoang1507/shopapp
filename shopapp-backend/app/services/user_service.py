from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User
from app.schemas.schemas import RegisterRequest, UserUpdate
from app.core.security import hash_password, verify_password


class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: RegisterRequest) -> User:
        user = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=hash_password(data.password),
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
        user = await UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, data: UserUpdate) -> User:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await db.flush()
        return user

    @staticmethod
    async def list_all(db: AsyncSession, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        from sqlalchemy import func
        total = await db.scalar(select(func.count()).select_from(User))
        result = await db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total
