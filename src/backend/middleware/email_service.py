"""
Email Service Middleware

Module này xử lý gửi email cho các chức năng như
forgot password, OTP, verification, notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime
import html

logger = logging.getLogger(__name__)


class EmailConfig:
    """Cấu hình cho email service"""

    # SMTP settings
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    # Authentication
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    # From settings
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@hanoi-travel.com")
    FROM_NAME = os.getenv("FROM_NAME", "Hanoi Travel")

    # Frontend URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://hanoi-travel.com")


class EmailTemplate:
    """Templates cho email"""

    @staticmethod
    def forgot_password_otp(otp: str, expiry_minutes: int = 10) -> Dict[str, str]:
        """Template cho forgot password OTP"""
        return {
            "subject": "Mã OTP đặt lại mật khẩu - Hanoi Travel",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Đặt lại mật khẩu - Hanoi Travel</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .otp {{ font-size: 32px; font-weight: bold; color: #e74c3c; text-align: center; padding: 20px; background: white; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏛️ Hanoi Travel</h1>
                        <p>Khám phá Hà Nội cùng chúng tôi</p>
                    </div>

                    <div class="content">
                        <h2>Xin chào,</h2>
                        <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản tại Hanoi Travel.</p>

                        <p><strong>Mã OTP của bạn là:</strong></p>
                        <div class="otp">{otp}</div>

                        <p><strong>Lưu ý:</strong></p>
                        <ul>
                            <li>Mã OTP có hiệu lực trong <strong>{expiry_minutes} phút</strong></li>
                            <li>Vui lòng không chia sẻ mã này với người khác</li>
                            <li>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này</li>
                        </ul>

                        <p>Nếu có vấn đề gì, vui lòng liên hệ với chúng tôi.</p>
                    </div>

                    <div class="footer">
                        <p>&copy; 2024 Hanoi Travel. All rights reserved.</p>
                        <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text": f"""
            Hanoi Travel - Đặt lại mật khẩu

            Xin chào,

            Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản tại Hanoi Travel.

            Mã OTP của bạn là: {otp}

            Thông tin:
            - Mã có hiệu lực trong {expiry_minutes} phút
            - Vui lòng không chia sẻ mã này với người khác
            - Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này

            Trân trọng,
            Đội ngũ Hanoi Travel
            """
        }

    @staticmethod
    def welcome_email(full_name: str, email: str) -> Dict[str, str]:
        """Template cho welcome email"""
        return {
            "subject": "Chào mừng đến với Hanoi Travel!",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Chào mừng - Hanoi Travel</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Chào mừng bạn!</h1>
                        <p>Tham gia cộng đồng Hanoi Travel</p>
                    </div>

                    <div class="content">
                        <h2>Chào mừng {html.escape(full_name)},</h2>
                        <p>Cảm ơn bạn đã đăng ký tài khoản tại Hanoi Travel!</p>

                        <p>Tại Hanoi Travel, bạn có thể:</p>
                        <ul>
                            <li>🗺️ Khám phá những địa điểm tuyệt đẹp của Hà Nội</li>
                            <li>📝 Chia sẻ trải nghiệm du lịch của bạn</li>
                            <li>👥 Kết nối với cộng đồng du lịch</li>
                            <li>🤖 Nhận gợi ý từ AI Chatbot thông minh</li>
                        </ul>

                        <p>Bắt đầu khám phá ngay!</p>
                        <center>
                            <a href="{EmailConfig.FRONTEND_URL}" class="btn">Khám phá ngay</a>
                        </center>
                    </div>

                    <div class="footer">
                        <p>&copy; 2024 Hanoi Travel. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text": f"""
            Chào mừng đến với Hanoi Travel!

            Chào mừng {full_name},

            Cảm ơn bạn đã đăng ký tài khoản tại Hanoi Travel!

            Tại Hanoi Travel, bạn có thể:
            - Khám phá những địa điểm tuyệt đẹp của Hà Nội
            - Chia sẻ trải nghiệm du lịch của bạn
            - Kết nối với cộng đồng du lịch
            - Nhận gợi ý từ AI Chatbot thông minh

            Truy cập {EmailConfig.FRONTEND_URL} để bắt đầu khám phá!

            Trân trọng,
            Đội ngũ Hanoi Travel
            """
        }

    @staticmethod
    def password_changed_notification(email: str) -> Dict[str, str]:
        """Template cho thông báo đổi mật khẩu"""
        return {
            "subject": "Thông báo: Mật khẩu của bạn đã được thay đổi",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Thông báo đổi mật khẩu - Hanoi Travel</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #e67e22; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔒 Thông báo bảo mật</h1>
                    </div>

                    <div class="content">
                        <h2>Mật khẩu của bạn đã được thay đổi</h2>

                        <div class="alert">
                            <strong>Thông báo:</strong> Mật khẩu cho tài khoản {email} đã được thay đổi thành công vào lúc {datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')}.
                        </div>

                        <p><strong>Nếu bạn thực hiện thay đổi này:</strong></p>
                        <ul>
                            <li>Không cần làm gì thêm</li>
                            <li>Bạn có thể đăng nhập bằng mật khẩu mới</li>
                        </ul>

                        <p><strong>Nếu bạn KHÔNG thực hiện thay đổi này:</strong></p>
                        <ul>
                            <li>Vui lòng liên hệ ngay với chúng tôi</li>
                            <li>Đăng nhập và kiểm tra tài khoản của bạn</li>
                            <li>Kiểm tra các hoạt động đáng ngờ khác</li>
                        </ul>

                        <p><strong>Để bảo vệ tài khoản:</strong></p>
                        <ul>
                            <li>Không chia sẻ mật khẩu với người khác</li>
                            <li>Sử dụng mật khẩu mạnh</li>
                            <li>Bật xác thực hai yếu tố nếu có</li>
                        </ul>
                    </div>

                    <div class="footer">
                        <p>&copy; 2024 Hanoi Travel. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text": f"""
            Thông báo đổi mật khẩu - Hanoi Travel

            Mật khẩu của bạn đã được thay đổi

            Thông báo: Mật khẩu cho tài khoản {email} đã được thay đổi thành công vào lúc {datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')}.

            Nếu bạn thực hiện thay đổi này:
            - Không cần làm gì thêm
            - Bạn có thể đăng nhập bằng mật khẩu mới

            Nếu bạn KHÔNG thực hiện thay đổi này:
            - Vui lòng liên hệ ngay với chúng tôi
            - Đăng nhập và kiểm tra tài khoản của bạn
            - Kiểm tra các hoạt động đáng ngờ khác

            Để bảo vệ tài khoản:
            - Không chia sẻ mật khẩu với người khác
            - Sử dụng mật khẩu mạnh
            - Bật xác thực hai yếu tố nếu có

            Trân trọng,
            Đội ngũ Hanoi Travel
            """
        }


class EmailService:
    """
    Service gửi email

    Cung cấp các phương thức gửi email với templates khác nhau.
    """

    def __init__(self, smtp_username: str = None, smtp_password: str = None,
                 smtp_host: str = None, smtp_port: int = None):
        """Khởi tạo email service"""
        # Use provided parameters or fall back to environment
        self.config = EmailConfig()
        self.config.SMTP_USERNAME = smtp_username or self.config.SMTP_USERNAME
        self.config.SMTP_PASSWORD = smtp_password or self.config.SMTP_PASSWORD
        self.config.SMTP_HOST = smtp_host or self.config.SMTP_HOST
        self.config.SMTP_PORT = smtp_port or self.config.SMTP_PORT

        self.is_configured = bool(
            self.config.SMTP_USERNAME and
            self.config.SMTP_PASSWORD and
            self.config.SMTP_HOST
        )

        if self.is_configured:
            logger.info("Email service configured successfully")
        else:
            logger.warning("Email service not properly configured")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str = None,
        text_content: str = None
    ) -> bool:
        """
        Gửi email

        Args:
            to_email: Email người nhận
            subject: Tiêu đề email
            html_content: Nội dung HTML
            text_content: Nội dung text (plain)

        Returns:
            bool: True nếu gửi thành công
        """
        if not self.is_configured:
            logger.warning("Email service not configured - skipping send")
            return True  # Return True để không block flow

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg['To'] = to_email

            # Add text content
            if text_content:
                msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

            # Add HTML content
            if html_content:
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # Send email
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                if self.config.SMTP_USE_TLS:
                    server.starttls()

                if self.config.SMTP_USERNAME and self.config.SMTP_PASSWORD:
                    server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)

                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_forgot_password_otp(self, email: str, otp: str) -> bool:
        """
        Gửi OTP cho forgot password

        Args:
            email: Email người nhận
            otp: Mã OTP

        Returns:
            bool: True nếu gửi thành công
        """
        template = EmailTemplate.forgot_password_otp(otp)
        return await self.send_email(
            to_email=email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )

    async def send_welcome_email(self, email: str, full_name: str) -> bool:
        """
        Gửi email chào mừng

        Args:
            email: Email người nhận
            full_name: Tên đầy đủ

        Returns:
            bool: True nếu gửi thành công
        """
        template = EmailTemplate.welcome_email(full_name, email)
        return await self.send_email(
            to_email=email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )

    async def send_password_changed_notification(self, email: str) -> bool:
        """
        Gửi thông báo đổi mật khẩu

        Args:
            email: Email người nhận

        Returns:
            bool: True nếu gửi thành công
        """
        template = EmailTemplate.password_changed_notification(email)
        return await self.send_email(
            to_email=email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )

    async def send_custom_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        is_html: bool = False
    ) -> bool:
        """
        Gửi email tùy chỉnh

        Args:
            to_email: Email người nhận
            subject: Tiêu đề email
            message: Nội dung email
            is_html: True nếu message là HTML

        Returns:
            bool: True nếu gửi thành công
        """
        if is_html:
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=message
            )
        else:
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                text_content=message
            )


# Global email service instance
email_service = EmailService()


# Utility functions
async def send_otp_email(email: str, otp: str) -> bool:
    """
    Shortcut để gửi OTP email

    Args:
        email: Email người nhận
        otp: Mã OTP

    Returns:
        bool: True nếu gửi thành công
    """
    return await email_service.send_forgot_password_otp(email, otp)


async def send_welcome_email_quick(email: str, full_name: str) -> bool:
    """
    Shortcut để gửi welcome email

    Args:
        email: Email người nhận
        full_name: Tên đầy đủ

    Returns:
        bool: True nếu gửi thành công
    """
    return await email_service.send_welcome_email(email, full_name)


def validate_email_format(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email cần kiểm tra

    Returns:
        bool: True nếu hợp lệ
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_email_for_logging(email: str) -> str:
    """
    Mask email cho logging purposes

    Args:
        email: Email cần mask

    Returns:
        str: Email đã mask
    """
    if '@' not in email:
        return email

    local, domain = email.split('@', 1)
    if len(local) <= 3:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        masked_local = local[:2] + '*' * (len(local) - 2)

    return f"{masked_local}@{domain}"