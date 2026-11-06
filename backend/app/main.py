"""EduGrade - FastAPI Application Entry Point."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Garante que a raiz do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.api.routes import (  # noqa: E402
    academic,
    access_requests,
    admin_settings,
    ai_correction,
    audit,
    auth,
    batch_grading,
    exams,
    imports,
    jobs,
    materials,
    quality,
    users,
)
from backend.app.core.config import settings  # noqa: E402
from backend.app.core.database import SessionLocal, init_db  # noqa: E402
from backend.app.core.exceptions import (  # noqa: E402
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    EduGradeException,
    ExternalServiceError,
    NotFoundError,
)
from backend.app.core.seed import seed_database  # noqa: E402

# Garantir existência dos diretórios do sistema
STORAGE_DIR = PROJECT_ROOT / "storage"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
LOGS_DIR = PROJECT_ROOT / "logs"


def _resolve_project_path(configured_path: str) -> Path:
    path = Path(configured_path)
    return path if path.is_absolute() else PROJECT_ROOT / path


for folder in [
    LOGS_DIR,
    STORAGE_DIR / "exams",
    STORAGE_DIR / "processed",
    STORAGE_DIR / "temp",
    STORAGE_DIR / "backups",
    _resolve_project_path(settings.upload_dir),
    _resolve_project_path(settings.pdf_dir),
    _resolve_project_path(settings.qr_dir),
    _resolve_project_path(settings.processed_dir),
    _resolve_project_path(settings.temp_dir),
    _resolve_project_path(settings.material_storage_dir),
    _resolve_project_path(settings.backup_dir),
]:
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as error:  # diretório somente leitura: avisa em vez de impedir o boot
        logging.getLogger("edugrade").warning(
            "Não foi possível criar o diretório %s: %s", folder, error
        )

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


def _database_display_url() -> str:
    """URL do banco sem credenciais, para exibir no log e no /health."""
    from sqlalchemy.engine import make_url

    try:
        return make_url(settings.database_url).render_as_string(hide_password=True)
    except Exception:  # pragma: no cover - URL inválida só falha na conexão
        return "<configuração inválida>"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação."""
    # Startup
    logger.info("Iniciando EduGrade...")
    logger.info("Banco de dados em uso: %s", _database_display_url())
    logger.info("Diretório de execução: %s", Path.cwd())
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


@app.middleware("http")
async def disable_frontend_cache(request: Request, call_next):
    """Evita que o navegador reutilize HTML/CSS/JS antigos após uma atualização."""
    response = await call_next(request)
    path = request.url.path.lower()
    if path in {"", "/"} or path.endswith((".html", ".css", ".js")):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


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
        "database": _database_display_url(),
        "working_directory": str(Path.cwd()),
    }


# Rotas da API
app.include_router(auth.router, prefix="/api/v1")
app.include_router(access_requests.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(users.students_router, prefix="/api/v1")
app.include_router(users.teachers_router, prefix="/api/v1")
app.include_router(academic.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(ai_correction.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(batch_grading.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(admin_settings.router, prefix="/api/v1")
app.include_router(quality.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")

# Frontend estático
if FRONTEND_DIR.is_dir():
    import re

    ASSET_REFERENCE = re.compile(r'(?P<attr>src|href)="(?P<url>[^"?]+\.(?:js|css))"')

    def _asset_version(url: str) -> str:
        """Versão do arquivo estático baseada na data de modificação."""
        clean = url.split("?", 1)[0].lstrip("/")
        asset = (FRONTEND_DIR / clean).resolve()
        try:
            return str(int(asset.stat().st_mtime))
        except OSError:
            return "0"

    def _render_html_with_versioned_assets(path: Path) -> HTMLResponse:
        """Injeta ?v=<mtime> em CSS/JS para o navegador nunca usar cache antigo."""
        html = path.read_text(encoding="utf-8")

        def replace(match: re.Match) -> str:
            url = match.group("url")
            if url.startswith(("http://", "https://", "//", "data:")):
                return match.group(0)
            return f'{match.group("attr")}="{url}?v={_asset_version(url)}"'

        return HTMLResponse(ASSET_REFERENCE.sub(replace, html))

    # Rota raiz redireciona para login.html
    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/login.html")

    @app.get("/{frontend_path:path}", include_in_schema=False)
    async def frontend_file_or_workspace(frontend_path: str):
        frontend_root = FRONTEND_DIR.resolve()
        requested_file = (frontend_root / frontend_path).resolve()
        if frontend_root not in requested_file.parents and requested_file != frontend_root:
            raise HTTPException(status_code=404, detail="Not Found")

        if requested_file.is_file():
            if requested_file.suffix.lower() == ".html":
                return _render_html_with_versioned_assets(requested_file)
            return FileResponse(requested_file)
        if requested_file.suffix.lower() == ".html":
            return _render_html_with_versioned_assets(FRONTEND_DIR / "workspace.html")
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
