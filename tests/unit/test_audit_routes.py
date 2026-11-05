from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.routes import audit as audit_routes
from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.main import app
from backend.app.models.audit import AuditActionType, AuditLog
from backend.app.models.user import User, UserRole


def test_recent_audit_serializes_sqlalchemy_audit_logs(monkeypatch):
    log = AuditLog(
        id=uuid4(),
        user_id=None,
        action=AuditActionType.LOGIN,
        entity_type="user",
        entity_id=uuid4(),
        description="Login successful",
        old_values=None,
        new_values=None,
        ip_address=None,
        user_agent=None,
        request_id=None,
        session_id=None,
        success=True,
        error_message=None,
        created_at=datetime.now(UTC),
    )

    class FakeAuditService:
        def __init__(self, _db):
            pass

        def get_recent_audit(self, hours, params):
            assert hours == 24
            return {
                "items": [log],
                "total": 1,
                "page": params.page,
                "page_size": params.page_size,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
            }

    monkeypatch.setattr(audit_routes, "AuditService", FakeAuditService)
    previous_admin_override = app.dependency_overrides.get(require_admin)
    previous_db_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[require_admin] = lambda: User(
        id=uuid4(),
        email="admin@example.test",
        username="admin",
        hashed_password="not-a-real-password",
        full_name="Admin",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
    )
    app.dependency_overrides[get_db] = lambda: object()
    try:
        response = TestClient(app).get("/api/v1/audit/recent")
    finally:
        if previous_admin_override is None:
            app.dependency_overrides.pop(require_admin, None)
        else:
            app.dependency_overrides[require_admin] = previous_admin_override
        if previous_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_db_override

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(log.id)
    assert body["items"][0]["action"] == "login"
    assert body["items"][0]["description"] == "Login successful"
