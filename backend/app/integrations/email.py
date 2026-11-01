"""Envio de e-mails transacionais."""

import smtplib
import ssl
from email.message import EmailMessage

from backend.app.core.config import settings


class EmailDeliveryError(Exception):
    """Falha explícita ao entregar uma mensagem por e-mail."""


def send_account_credentials(
    email: str,
    full_name: str,
    username: str,
    password: str,
) -> None:
    if not settings.smtp_host:
        raise EmailDeliveryError(
            "O SMTP não está configurado. Configure SMTP_HOST para enviar a senha ao solicitante."
        )
    if bool(settings.smtp_user) != bool(settings.smtp_password):
        raise EmailDeliveryError("A configuração de autenticação SMTP está incompleta.")

    message = EmailMessage()
    message["Subject"] = "Seu acesso ao EduGrade foi aprovado"
    message["From"] = settings.email_from
    message["To"] = email
    message.set_content(
        f"""Olá, {full_name}.

Seu acesso ao EduGrade foi aprovado.

Usuário: {username}
Senha temporária: {password}

Por segurança, entre no sistema e altere sua senha assim que possível.
"""
    )

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=20,
                context=ssl.create_default_context(),
            ) as server:
                if settings.smtp_user:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("Não foi possível enviar o e-mail com as credenciais.") from exc
