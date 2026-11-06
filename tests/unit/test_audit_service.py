from unittest.mock import MagicMock
from uuid import uuid4

from backend.app.models.audit import AuditActionType
from backend.app.schemas.common import PaginationParams
from backend.app.services.audit_service import AuditService, SystemLogService


def test_audit_service_forwards_log_and_paginated_queries():
    service = AuditService(MagicMock())
    service.repo = MagicMock()
    user_id, entity_id = uuid4(), uuid4()
    log = object()
    service.repo.log.return_value = log

    assert service.log_action(
        AuditActionType.LOGIN,
        "login",
        user_id=user_id,
        entity_type="user",
        entity_id=entity_id,
        new_values={"active": True},
    ) is log
    service.repo.log.assert_called_once()

    params = PaginationParams(page=2, page_size=1)
    second_log = object()
    service.repo.get_by_user.return_value = [log, second_log]
    result = service.get_user_audit(user_id, params)
    assert result.total == 2
    assert result.items == [log, second_log]
    assert result.page == 2
    assert result.has_prev is True
    service.repo.get_by_user.assert_called_once_with(user_id, limit=1)

    service.repo.get_by_entity.return_value = [log]
    assert service.get_entity_audit("user", entity_id, params).total == 1
    service.repo.get_by_action.return_value = [log]
    assert service.get_action_audit(AuditActionType.LOGIN, params).total == 1


def test_audit_service_recent_defaults_and_system_logs():
    service = AuditService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_recent.return_value = []

    result = service.get_recent_audit()

    assert result.total == 0
    service.repo.get_recent.assert_called_once_with(hours=24, limit=20)

    system_logs = SystemLogService(MagicMock())
    system_logs.repo = MagicMock()
    expected_log = object()
    system_logs.repo.log.return_value = expected_log
    assert system_logs.log(
        "ERROR",
        "tests",
        "failed",
        module="unit",
        context={"code": 1},
    ) is expected_log
    system_logs.repo.log.assert_called_once()
    system_logs.repo.get_errors.return_value = [expected_log]
    assert system_logs.get_errors(hours=2, limit=5) == [expected_log]
    system_logs.repo.get_errors.assert_called_once_with(hours=2, limit=5)
