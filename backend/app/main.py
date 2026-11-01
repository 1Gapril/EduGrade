"""EduGrade - FastAPI Application Entry Point."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import init_db, SessionLocal
from backend.app.core.seed import seed_database
from backend.app.api.routes import (
    access_requests,
    auth,
    users,
    academic,
    exams,
    ai_correction,
    audit,
    batch_grading,
    materials,
    admin_settings,
)
from backend.app.core.exceptions import (
    EduGradeException, ValidationError, NotFoundError,
    ConflictError, AuthenticationError, AuthorizationError,
    ExternalServiceError, BusinessRuleError, FileProcessingError
)

# Garantir existência dos diretórios do sistema
STORAGE_DIR = PROJECT_ROOT / "storage"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
LOGS_DIR = PROJECT_ROOT / "logs"

for folder in [
    LOGS_DIR,
    STORAGE_DIR / "exams",
    STORAGE_DIR / "processed",
    STORAGE_DIR / "temp",
    STORAGE_DIR / "backups",
]:
    folder.mkdir(parents=True, exist_ok=True)

# Configuração de logging
log_handlers = [logging.StreamHandler(sys.stdout)]
if settings.log_file:
    log_path = Path(settings.log_file)
    if not log_path.is_absolute():
        log_path = PROJECT_ROOT / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handlers.append(logging.FileHandler(str(log_path), encoding="utf-8"))

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers,
)
logger = logging.getLogger("edugrade")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação."""
    # Startup
    logger.info("Iniciando EduGrade...")
    try:
        init_db()
        logger.info("Banco de dados inicializado.")
        
        # Popula dados de demonstração se banco estiver vazio
        db = SessionLocal()
        try:
            from backend.app.services.admin_settings_service import apply_persisted_runtime_settings

            apply_persisted_runtime_settings(db)
            seed_database(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")

    yield

    # Shutdown
    logger.info("Encerrando EduGrade...")
    from backend.app.services.ai_correction_service import AIProviderFactory
    await AIProviderFactory.close_all()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de Gestão e Desempenho Acadêmico com IA para Correção de Provas",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(EduGradeException)
async def edigrade_exception_handler(request: Request, exc: EduGradeException):
    status_code = 400
    if isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, AuthenticationError):
        status_code = 401
    elif isinstance(exc, AuthorizationError):
        status_code = 403
    elif isinstance(exc, ConflictError):
        status_code = 409
    elif isinstance(exc, ExternalServiceError):
        status_code = 502
    elif isinstance(exc, BusinessRuleError):
        status_code = 422

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Erro não tratado")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Erro interno do servidor" if not settings.debug else str(exc),
        },
    )


# Health check
@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# Rotas da API
app.include_router(auth.router, prefix="/api/v1")
app.include_router(access_requests.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(academic.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(ai_correction.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(batch_grading.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(admin_settings.router, prefix="/api/v1")

# Frontend estático
if FRONTEND_DIR.is_dir():
    # Rota raiz redireciona para login.html
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/login.html")

    @app.get("/{frontend_path:path}", include_in_schema=False)
    async def frontend_file_or_workspace(frontend_path: str):
        frontend_root = FRONTEND_DIR.resolve()
        requested_file = (frontend_root / frontend_path).resolve()
        if frontend_root not in requested_file.parents:
            raise HTTPException(status_code=404, detail="Not Found")

        if requested_file.is_file():
            return FileResponse(requested_file)
        if requested_file.suffix.lower() == ".html":
            return FileResponse(FRONTEND_DIR / "workspace.html")
        raise HTTPException(status_code=404, detail="Not Found")

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
