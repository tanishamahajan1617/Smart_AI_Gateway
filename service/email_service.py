import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import settings


class EmailService:

    @staticmethod
    def send_password_reset_email(
        email: str,
        token: str
    ) -> None:

        reset_link = (
            f"{settings.FRONTEND_URL}"
            f"/reset-password?token={token}"
        )

        message = MIMEMultipart("alternative")

        message["Subject"] = "Reset Your Password"

        message["From"] = settings.SMTP_FROM

        message["To"] = email

        html = f"""
        <html>
            <body>
                <h2>Smart AI Gateway</h2>

                <p>Hello,</p>

                <p>
                    We received a request to reset your password.
                </p>

                <p>
                    Click the link below:
                </p>

                <p>
                    <a href="{reset_link}">
                        Reset Password
                    </a>
                </p>

                <p>
                    This link expires in 30 minutes.
                </p>

                <p>
                    If you did not request this, please ignore this email.
                </p>

            </body>
        </html>
        """

        message.attach(
            MIMEText(
                html,
                "html"
            )
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            server.send_message(message)