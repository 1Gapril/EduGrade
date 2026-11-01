"""Rotas de Autenticação."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_active_user
from backend.app.models.user import User
from backend.app.schemas.user import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse, UserUpdatePassword
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """Login de usuário (suporta JSON e FormData)."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        login_data = LoginRequest(**body)
    else:
        form = await request.form()
        login_data = LoginRequest(
            username=str(form.get("username", "")),
            password=str(form.get("password", "")),
        )
    auth_service = AuthService(db)
    return auth_service.authenticate(login_data)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Renova access token."""
    auth_service = AuthService(db)
    return auth_service.refresh_token(request.refresh_token)


@router.post("/change-password")
def change_password(
    data: UserUpdatePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Altera senha do usuário logado."""
    auth_service = AuthService(db)
    auth_service.change_password(current_user.id, data.current_password, data.new_password)
    return {"message": "Senha alterada com sucesso"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Retorna informações do usuário logado."""
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """Logout (client-side - apenas invalida token no frontend)."""
    return {"message": "Logout realizado com sucesso"}