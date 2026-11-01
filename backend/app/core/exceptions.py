"""Exceções customizadas do EduGrade."""


class EduGradeException(Exception):
    """Exceção base do EduGrade."""
    def __init__(self, message: str, code: str = None, detail: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.detail = detail
        super().__init__(message)


class ValidationError(EduGradeException):
    """Erro de validação de dados."""
    pass


class NotFoundError(EduGradeException):
    """Recurso não encontrado."""
    pass


class ConflictError(EduGradeException):
    """Conflito (duplicidade, etc.)."""
    pass


class AuthenticationError(EduGradeException):
    """Erro de autenticação."""
    pass


class AuthorizationError(EduGradeException):
    """Erro de autorização/permissão."""
    pass


class ExternalServiceError(EduGradeException):
    """Erro em serviço externo (IA, OCR, etc.)."""
    pass


class BusinessRuleError(EduGradeException):
    """Violação de regra de negócio."""
    pass


class FileProcessingError(EduGradeException):
    """Erro no processamento de arquivo."""
    pass