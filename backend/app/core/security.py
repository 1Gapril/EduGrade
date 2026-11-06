"""Segurança: Hash de senhas, JWT, dependências de autenticação."""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repository import UserRepository

# Hash de senhas
pwd_context = CryptContext(schemes=[settings.password_hash_algorithm], deprecated="auto")

# Esquema OAuth2 — aponta para o endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    """Schema de resposta de token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Dados decodificados do token."""
    sub: str | None = None
    role: str | None = None
    user_id: UUID | None = None
    exp: datetime | None = None


class TokenPayload(BaseModel):
    """Payload do JWT."""
    sub: str  # user email/username
    role: str
    user_id: str
    type: str = "access"  # access ou refresh
    exp: int
    iat: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    role: str,
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Cria token de acesso JWT."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = TokenPayload(
        sub=subject,
        role=role,
        user_id=str(user_id),
        type="access",
        exp=int(expire.timestamp()),
        iat=int(now.timestamp()),
    )
    return jwt.encode(payload.model_dump(), settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str,
    role: str,
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Cria token de refresh JWT."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload = TokenPayload(
        sub=subject,
        role=role,
        user_id=str(user_id),
        type="refresh",
        exp=int(expire.timestamp()),
        iat=int(now.timestamp()),
    )
    return jwt.encode(payload.model_dump(), settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload:
    """Decodifica e valida token JWT."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Obtém usuário atual a partir do token de acesso."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload.type != "access":
            raise credentials_exception
    except (JWTError, ValueError) as error:
        raise credentials_exception from error

    user_repo = UserRepository(db)
    user = user_repo.get(UUID(payload.user_id))
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Garante que o usuário está ativo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """Dependency factory para exigir roles específicas."""
    def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta operação",
            )
        return current_user
    return role_checker


# Shortcuts para roles comuns
require_admin = require_role(UserRole.ADMIN)
require_teacher = require_role(UserRole.TEACHER, UserRole.ADMIN)
require_student = require_role(UserRole.STUDENT)
require_teacher_or_admin = require_role(UserRole.TEACHER, UserRole.ADMIN)
require_any_authenticated = require_role(UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN)
