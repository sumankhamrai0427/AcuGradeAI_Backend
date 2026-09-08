"""Email controller for AcuGrade AI.

Handles background dispatching of transactional emails such as:
- Account Registration (Welcome Email)
- Normal Login Notification
- Google Login Notification
"""

import os
import smtplib
import threading
from datetime import datetime
from email.message import EmailMessage
from utils.config import config
from utils.logger import logger


def render_email_template(title: str, content_html: str) -> str:
    """Create a modern, responsive HTML email template for AcuGrade AI."""
    app_name = config.APP_NAME or "AcuGrade AI"
    current_year = datetime.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}
        .wrapper {{
            max-width: 600px;
            margin: 30px auto;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            border: 1px solid #e2e8f0;
        }}
        .header {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            padding: 32px 36px;
            text-align: center;
            color: #ffffff;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header p {{
            margin: 8px 0 0;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
        }}
        .body-content {{
            padding: 36px;
            font-size: 15px;
            line-height: 1.65;
            color: #334155;
        }}
        .card {{
            background: #f1f5f9;
            border-left: 4px solid #6366f1;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #f8fafc;
            padding: 24px 36px;
            text-align: center;
            font-size: 12px;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }}
        .footer p {{
            margin: 4px 0;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>🎓 {app_name}</h1>
            <p>AI-Powered Adaptive Learning & Progress Analytics</p>
        </div>
        <div class="body-content">
            {content_html}
        </div>
        <div class="footer">
            <p><strong>{app_name}</strong> &bull; Personalized Learning Ecosystem</p>
            <p>&copy; {current_year} {app_name}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def _send_email_sync(to_email: str, subject: str, content_html: str, plain_text: str = "") -> bool:
    """Synchronously dispatches the email via SMTP."""
    try:
        smtp_server = config.SMTP_SERVER or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(config.SMTP_PORT or os.getenv("SMTP_PORT", "587"))
        smtp_username = config.SMTP_USERNAME or os.getenv("SMTP_USERNAME")
        smtp_password = config.SMTP_PASSWORD or os.getenv("SMTP_PASSWORD")
        smtp_sender_name = config.SMTP_SENDER_NAME or os.getenv("SMTP_SENDER_NAME", "AcuGrade AI")
        smtp_use_tls = config.SMTP_USE_TLS if hasattr(config, "SMTP_USE_TLS") else True

        if not smtp_username or not smtp_password:
            logger.warning(f"[EMAIL] SMTP credentials not configured. Skipped sending email to {to_email}")
            return False

        html_body = render_email_template(subject, content_html)

        message = EmailMessage()
        message["From"] = f"{smtp_sender_name} <{smtp_username}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Plain-text version
        text_body = plain_text or "Please view this email in an HTML-compatible client."
        message.set_content(text_body)

        # HTML version
        message.add_alternative(html_body, subtype="html")

        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        logger.info(f"[EMAIL] Successfully sent email '{subject}' to {to_email}")
        return True

    except Exception as e:
        logger.error(f"[EMAIL] Failed to send email to {to_email}: {str(e)}")
        return False


def send_email_async(to_email: str, subject: str, content_html: str, plain_text: str = "") -> None:
    """Dispatches email asynchronously in a background thread so the HTTP request is not blocked."""
    thread = threading.Thread(
        target=_send_email_sync,
        args=(to_email, subject, content_html, plain_text),
        daemon=True,
    )
    thread.start()


def send_email(to_email: str) -> bool:
    """Standard send_email function for login success notification."""
    subject = "Login Successful - AcuGrade AI"
    content_html = """
        <h2 style="color: #1e293b; margin-top: 0;">Welcome back to AcuGrade AI! 🎓</h2>
        <p>You have successfully logged in to your <strong>AcuGrade AI</strong> account.</p>
        <div class="card">
            <p style="margin: 0; font-size: 14px; color: #475569;">
                📍 <strong>Security Notice:</strong> If this was not you, please secure your account immediately by resetting your password.
            </p>
        </div>
        <p>Continue your learning journey and make progress every day!</p>
        <p><strong>Happy Learning! 🚀</strong></p>
    """
    plain_text = (
        "Welcome back to AcuGrade AI!\n\n"
        "You have successfully logged in to your account.\n\n"
        "If this was not you, please secure your account immediately.\n\n"
        "Happy Learning!\nAcuGrade AI Team"
    )
    send_email_async(to_email, subject, content_html, plain_text)
    return True


def send_registration_email(to_email: str, name: str = "", username: str = "", role_name: str = "PARENT") -> bool:
    """Sends a personalized welcome email upon successful account registration."""
    display_name = name.strip() if name else "Learner"
    subject = "Welcome to AcuGrade AI! 🎓 Your Account is Ready"

    username_info = f"<p><strong>Username:</strong> <code>{username}</code></p>" if username else ""
    role_info = f"<p><strong>Role:</strong> {role_name.title()}</p>" if role_name else ""

    content_html = f"""
        <h2 style="color: #1e293b; margin-top: 0;">Welcome aboard, {display_name}! 🎉</h2>
        <p>Thank you for joining <strong>AcuGrade AI</strong>. Your account has been created successfully.</p>
        
        <div class="card">
            <h3 style="margin-top: 0; font-size: 15px; color: #334155;">📋 Account Details:</h3>
            <p style="margin: 4px 0;"><strong>Email:</strong> {to_email}</p>
            {username_info}
            {role_info}
        </div>

        <p>With AcuGrade AI, you can:</p>
        <ul style="color: #475569; padding-left: 20px;">
            <li>Track real-time learning analytics and skill mastery.</li>
            <li>Experience AI-generated practice exams & adaptive learning paths.</li>
            <li>Collaborate with teachers, parents, and students seamlessly.</li>
        </ul>

        <p>Get started today and unlock the power of AI-assisted education!</p>
        <p><strong>Best regards,</strong><br>The AcuGrade AI Team</p>
    """

    plain_text = (
        f"Welcome aboard, {display_name}!\n\n"
        f"Thank you for registering on AcuGrade AI.\n"
        f"Email: {to_email}\n"
        f"Username: {username}\n"
        f"Role: {role_name}\n\n"
        f"Best regards,\nThe AcuGrade AI Team"
    )

    send_email_async(to_email, subject, content_html, plain_text)
    return True


def send_login_email(to_email: str, name: str = "", login_type: str = "Standard") -> bool:
    """Sends a login alert email for Standard Login or Google OAuth Login."""
    display_name = name.strip() if name else "User"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    subject = f"Login Alert ({login_type}) - AcuGrade AI"

    content_html = f"""
        <h2 style="color: #1e293b; margin-top: 0;">Hello, {display_name}! 🎓</h2>
        <p>You have successfully logged in to your <strong>AcuGrade AI</strong> account.</p>
        
        <div class="card">
            <p style="margin: 4px 0;"><strong>Login Method:</strong> {login_type} Sign-in</p>
            <p style="margin: 4px 0;"><strong>Timestamp:</strong> {current_time}</p>
            <p style="margin: 4px 0; font-size: 13px; color: #64748b;">If this login was made by you, no further action is needed.</p>
        </div>

        <p style="color: #475569;">
            If you did not perform this action, please change your password or contact our support team immediately.
        </p>
        <p><strong>Happy Learning! 🚀</strong><br>The AcuGrade AI Team</p>
    """

    plain_text = (
        f"Hello {display_name}!\n\n"
        f"You have successfully logged in to AcuGrade AI via {login_type} Sign-in at {current_time}.\n\n"
        f"If this was not you, please secure your account immediately.\n\n"
        f"Happy Learning!\nThe AcuGrade AI Team"
    )

    send_email_async(to_email, subject, content_html, plain_text)
    return True
