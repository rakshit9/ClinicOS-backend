"""Email service for sending notifications."""

from typing import Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from loguru import logger

from app.config import settings


class EmailService:
    """Email service for sending notifications."""
    
    def __init__(self):
        """Initialize email service."""
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_STARTTLS=settings.mail_tls,
            MAIL_SSL_TLS=not settings.mail_tls,
            USE_CREDENTIALS=bool(settings.mail_username and settings.mail_password),
            VALIDATE_CERTS=True,
        )
        self.fastmail = FastMail(self.config)
    
    async def send_reset_email(self, email: str, reset_link: str) -> bool:
        """Send password reset email."""
        try:
            # If no email credentials, log to console (dev mode)
            if not settings.mail_username or not settings.mail_password:
                logger.info(f"Password reset link for {email}: {reset_link}")
                return True
            
            message = MessageSchema(
                subject="Password Reset - Clinic Auth",
                recipients=[email],
                body=f"""
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in {settings.reset_token_expires_min} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                """,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send reset email to {email}: {e}")
            return False


# Global email service instance
email_service = EmailService()
