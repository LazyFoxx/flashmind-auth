# from uuid import UUID
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update
# from typing import Optional
# from domain.value_objects.email import Email
# from src.application.interfaces import AbstractUserRepository

# from domain.entities import User

# from models import UserModel


# class SQLAlchemyUserRepository(AbstractUserRepository):
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def get_by_id(self, user_id: UUID) -> Optional[User]:
#         stmt = select(UserModel).where(UserModel.id == user_id)
#         result = await self.session.execute(stmt)
#         db_user = result.scalar_one_or_none()
#         return db_user.to_domain() if db_user else None

#     async def get_by_email(self, email: Email) -> Optional[User]:
#         stmt = select(UserModel).where(UserModel.email == email)
#         result = await self.session.execute(stmt)
#         db_user = result.scalar_one_or_none()
#         return db_user.to_domain() if db_user else None

#     async def add(self, user: User) -> None:
#         db_user = UserModel.from_domain(user)
#         self.session.add(db_user)
#         try:
#             await self.session.flush()  # или commit в Unit of Work
#         except IntegrityError as exc:
#             # Обычно дубликат уникального поля (email)
#             if (
#                 "unique" in str(exc.orig).lower()
#                 or "duplicate" in str(exc.orig).lower()
#             ):
#                 raise UserAlreadyExistsError(user.email) from exc
#             raise DatabaseError("Integrity violation while adding user") from exc
#         except Exception as exc:
#             raise DatabaseError("Failed to add user") from exc

#     async def set_password(self, user_id: UUID, hashed_password: str) -> None:
#         try:
#             stmt = (
#                 update(UserModel)
#                 .where(UserModel.id == user_id)
#                 .values(hashed_password=hashed_password)
#             )
#             result = await self.session.execute(stmt)
#             if result.rowcount == 0:
#                 raise UserNotFoundError(user_id=user_id)
#         except Exception as exc:
#             raise DatabaseError("Failed to set password") from exc
