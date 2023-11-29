from typing import Optional

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, IntegerIDMixin, exceptions, models,
                           schemas)

from src.auth.models import User
from src.auth.utils import get_user_db
from src.config import SECRET_AUTH


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Выполняется после регистрации пользователя.
        Можно отправить письмо пользователю и/или администратору
        :param user: Модель пользователя
        :param request: Запрос
        :return: None
        """
        print(f"User {user.id} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        """
        Метод создания пользователя
        :param user_create: Схема для валидации??
        :param safe: Если значение True, is_superuser или is_verified, будут игнорироваться во время создания,
                     по умолчанию установлено значение False.
        :param request: Запрос
        :return: Созданный пользователь
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )

        # Вырезаем пароль
        password = user_dict.pop("password")

        # Шифруем пароль
        user_dict["hashed_password"] = self.password_helper.hash(password)

        # Назначаем роль по умолчанию
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
