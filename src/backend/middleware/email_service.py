"""
Email Service Middleware

Module này xử lý gửi email cho các chức năng:
- Welcome email khi đăng ký
- Password reset email (forgot password)  
- Password changed notification
Sử dụng SendGrid API (HTTP) để gửi email.
"""

from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime
import html

logger = logging.getLogger(__name__)


class EmailConfig:
    """
    Cấu hình cho email service (SendGrid)
    
    Env vars:
        SENDGRID_API_KEY: API key từ SendGrid
        FROM_EMAIL: Email gửi đi (phải verify trên SendGrid)
        FROM_NAME: Tên hiển thị
        FRONTEND_URL: URL frontend cho các link trong email
    """

    # SendGrid API Key
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
    
    # From settings
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@hanoi-travel.com")
    FROM_NAME = os.getenv("FROM_NAME", "Hanoi Travel")

    # Frontend URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class EmailTemplate:
    """Templates cho email - Modern Design với tiếng Việt"""

    # Base CSS styles dùng chung cho tất cả emails
    BASE_STYLES = """
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.8; 
            color: #2d3748; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
        }
        .email-wrapper {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .header p {
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .header .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .content {
            padding: 40px 35px;
        }
        .content h2 {
            color: #1a202c;
            font-size: 22px;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .content p {
            color: #4a5568;
            font-size: 16px;
            margin-bottom: 18px;
        }
        .highlight-box {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-left: 4px solid #667eea;
            padding: 20px 25px;
            border-radius: 12px;
            margin: 25px 0;
        }
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 25px 0;
        }
        .feature-list li {
            padding: 12px 0;
            padding-left: 35px;
            position: relative;
            color: #4a5568;
            font-size: 15px;
        }
        .feature-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #48bb78;
            font-weight: bold;
            font-size: 18px;
        }
        .btn-primary {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 16px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.35);
        }
        .btn-container {
            text-align: center;
            margin: 35px 0;
        }
        .alert-box {
            background: linear-gradient(135deg, #fef3cd 0%, #ffeeba 100%);
            border: 1px solid #f0d78e;
            padding: 20px 25px;
            border-radius: 12px;
            margin: 25px 0;
        }
        .alert-box.warning {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            border-color: #fc8181;
        }
        .divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #e2e8f0, transparent);
            margin: 30px 0;
        }
        .footer {
            background: #f7fafc;
            text-align: center;
            padding: 30px;
            border-top: 1px solid #e2e8f0;
        }
        .footer p {
            color: #718096;
            font-size: 14px;
            margin: 5px 0;
        }
        .small-text {
            font-size: 13px;
            color: #a0aec0;
        }
    """

    @staticmethod
    def welcome_email(full_name: str, email: str) -> Dict[str, str]:
        """Template cho welcome email - Modern Vietnamese Design"""
        escaped_name = html.escape(full_name)
        escaped_email = html.escape(email)
        frontend_url = EmailConfig.FRONTEND_URL
        
        return {
            "subject": "🎉 Chào mừng bạn đến với Hanoi Travel!",
            "html": f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chào mừng - Hanoi Travel</title>
    <style>{EmailTemplate.BASE_STYLES}</style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header">
            <div class="icon">🏛️</div>
            <h1>Chào mừng đến với Hanoi Travel!</h1>
            <p>Khám phá vẻ đẹp ngàn năm của Thủ đô</p>
        </div>

        <div class="content">
            <h2>Xin chào {escaped_name}! 👋</h2>
            
            <p>Cảm ơn bạn đã tạo tài khoản tại <strong>Hanoi Travel</strong> - nền tảng khám phá du lịch Hà Nội hàng đầu!</p>
            
            <div class="highlight-box">
                <strong>🎁 Tài khoản của bạn đã được kích hoạt thành công!</strong><br>
                <span class="small-text">Email: {escaped_email}</span>
            </div>

            <p>Với Hanoi Travel, bạn có thể:</p>
            
            <ul class="feature-list">
                <li>Khám phá hơn 1000+ địa điểm du lịch tuyệt đẹp tại Hà Nội</li>
                <li>Chia sẻ trải nghiệm và đánh giá các điểm đến yêu thích</li>
                <li>Kết nối với cộng đồng du lịch sôi động</li>
                <li>Nhận gợi ý thông minh từ AI Chatbot về lịch trình du lịch</li>
                <li>Lưu lại những địa điểm yêu thích để khám phá sau</li>
            </ul>

            <div class="btn-container">
                <a href="{frontend_url}" class="btn-primary">
                    🚀 Bắt đầu khám phá ngay
                </a>
            </div>

            <div class="divider"></div>

            <p class="small-text" style="text-align: center;">
                Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi nhé!
            </p>
        </div>

        <div class="footer">
            <p><strong>Hanoi Travel</strong> - Khám phá Hà Nội theo cách của bạn</p>
            <p>© 2024 Hanoi Travel. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Chào mừng đến với Hanoi Travel!

Xin chào {full_name}!

Cảm ơn bạn đã tạo tài khoản tại Hanoi Travel - nền tảng khám phá du lịch Hà Nội hàng đầu!

Tài khoản của bạn đã được kích hoạt thành công!
Email: {email}

Với Hanoi Travel, bạn có thể:
• Khám phá hơn 1000+ địa điểm du lịch tuyệt đẹp tại Hà Nội
• Chia sẻ trải nghiệm và đánh giá các điểm đến yêu thích
• Kết nối với cộng đồng du lịch sôi động
• Nhận gợi ý thông minh từ AI Chatbot về lịch trình du lịch
• Lưu lại những địa điểm yêu thích để khám phá sau

Truy cập {frontend_url} để bắt đầu khám phá!

Trân trọng,
Đội ngũ Hanoi Travel
            """
        }

    @staticmethod
    def password_reset_email(full_name: str, email: str, reset_url: str) -> Dict[str, str]:
        """Template cho password reset email - Modern Vietnamese Design"""
        escaped_name = html.escape(full_name)
        escaped_email = html.escape(email)
        
        return {
            "subject": "🔐 Đặt lại mật khẩu - Hanoi Travel",
            "html": f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đặt lại mật khẩu - Hanoi Travel</title>
    <style>{EmailTemplate.BASE_STYLES}</style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header" style="background: linear-gradient(135deg, #e53e3e 0%, #dd6b20 100%);">
            <div class="icon">🔐</div>
            <h1>Yêu cầu đặt lại mật khẩu</h1>
            <p>Bảo mật tài khoản của bạn</p>
        </div>

        <div class="content">
            <h2>Xin chào {escaped_name}!</h2>
            
            <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản Hanoi Travel của bạn.</p>

            <div class="highlight-box">
                <strong>📧 Tài khoản:</strong> {escaped_email}<br>
                <strong>⏰ Thời hạn:</strong> Link có hiệu lực trong <strong>1 giờ</strong>
            </div>

            <p>Nhấn vào nút bên dưới để đặt lại mật khẩu:</p>

            <div class="btn-container">
                <a href="{reset_url}" class="btn-primary" style="background: linear-gradient(135deg, #e53e3e 0%, #dd6b20 100%);">
                    🔑 Đặt lại mật khẩu ngay
                </a>
            </div>

            <p class="small-text" style="text-align: center; word-break: break-all;">
                Hoặc copy đường dẫn này vào trình duyệt:<br>
                <a href="{reset_url}" style="color: #667eea;">{reset_url}</a>
            </p>

            <div class="divider"></div>

            <div class="alert-box warning">
                <strong>⚠️ Lưu ý bảo mật:</strong><br>
                • Nếu bạn <strong>không yêu cầu</strong> đặt lại mật khẩu, vui lòng bỏ qua email này<br>
                • Không chia sẻ đường dẫn này với bất kỳ ai<br>
                • Đường dẫn sẽ hết hạn sau 1 giờ
            </div>
        </div>

        <div class="footer">
            <p><strong>Hanoi Travel</strong> - Khám phá Hà Nội theo cách của bạn</p>
            <p>© 2024 Hanoi Travel. All rights reserved.</p>
            <p class="small-text">Đây là email tự động, vui lòng không trả lời email này.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Yêu cầu đặt lại mật khẩu - Hanoi Travel

Xin chào {full_name}!

Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản Hanoi Travel của bạn.

Tài khoản: {email}
Thời hạn: Link có hiệu lực trong 1 giờ

Để đặt lại mật khẩu, vui lòng truy cập đường dẫn sau:
{reset_url}

LƯU Ý BẢO MẬT:
• Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này
• Không chia sẻ đường dẫn này với bất kỳ ai
• Đường dẫn sẽ hết hạn sau 1 giờ

Trân trọng,
Đội ngũ Hanoi Travel
            """
        }

    @staticmethod
    def password_changed_notification(email: str) -> Dict[str, str]:
        """Template cho thông báo đổi mật khẩu - Modern Vietnamese Design"""
        current_time = datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')
        escaped_email = html.escape(email)
        
        return {
            "subject": "✅ Mật khẩu đã được thay đổi - Hanoi Travel",
            "html": f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thông báo đổi mật khẩu - Hanoi Travel</title>
    <style>{EmailTemplate.BASE_STYLES}</style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header" style="background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);">
            <div class="icon">✅</div>
            <h1>Mật khẩu đã được thay đổi</h1>
            <p>Thông báo bảo mật tài khoản</p>
        </div>

        <div class="content">
            <h2>Xin chào!</h2>
            
            <div class="highlight-box" style="border-left-color: #38a169;">
                <strong>🔒 Thông báo:</strong><br>
                Mật khẩu cho tài khoản <strong>{escaped_email}</strong> đã được thay đổi thành công.<br>
                <span class="small-text">Thời gian: {current_time}</span>
            </div>

            <h3 style="color: #38a169;">✓ Nếu bạn thực hiện thay đổi này:</h3>
            <ul class="feature-list">
                <li>Không cần thực hiện thêm bất kỳ hành động nào</li>
                <li>Bạn có thể đăng nhập bằng mật khẩu mới</li>
            </ul>

            <div class="alert-box warning">
                <strong>⚠️ Nếu bạn KHÔNG thực hiện thay đổi này:</strong><br><br>
                Vui lòng thực hiện ngay các bước sau:<br>
                • Liên hệ với chúng tôi ngay lập tức<br>
                • Đăng nhập và kiểm tra tài khoản của bạn<br>
                • Kiểm tra các hoạt động đáng ngờ khác
            </div>

            <div class="divider"></div>

            <h3>🛡️ Mẹo bảo mật tài khoản:</h3>
            <ul class="feature-list">
                <li>Không chia sẻ mật khẩu với bất kỳ ai</li>
                <li>Sử dụng mật khẩu mạnh với số và ký tự đặc biệt</li>
                <li>Đổi mật khẩu định kỳ</li>
                <li>Không sử dụng lại mật khẩu ở nhiều trang web</li>
            </ul>
        </div>

        <div class="footer">
            <p><strong>Hanoi Travel</strong> - Khám phá Hà Nội theo cách của bạn</p>
            <p>© 2024 Hanoi Travel. All rights reserved.</p>
            <p class="small-text">Đây là email tự động từ hệ thống bảo mật.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Thông báo: Mật khẩu đã được thay đổi - Hanoi Travel

Xin chào!

THÔNG BÁO: Mật khẩu cho tài khoản {email} đã được thay đổi thành công.
Thời gian: {current_time}

NẾU BẠN THỰC HIỆN THAY ĐỔI NÀY:
• Không cần thực hiện thêm bất kỳ hành động nào
• Bạn có thể đăng nhập bằng mật khẩu mới

NẾU BẠN KHÔNG THỰC HIỆN THAY ĐỔI NÀY:
Vui lòng thực hiện ngay các bước sau:
• Liên hệ với chúng tôi ngay lập tức
• Đăng nhập và kiểm tra tài khoản của bạn
• Kiểm tra các hoạt động đáng ngờ khác

MẸO BẢO MẬT TÀI KHOẢN:
• Không chia sẻ mật khẩu với bất kỳ ai
• Sử dụng mật khẩu mạnh với số và ký tự đặc biệt
• Đổi mật khẩu định kỳ
• Không sử dụng lại mật khẩu ở nhiều trang web

Trân trọng,
Đội ngũ Hanoi Travel
            """
        }


class EmailService:
    """
    Service gửi email

    Cung cấp các phương thức gửi email với templates khác nhau.
    """

    def __init__(self):
        """Khởi tạo email service với SendGrid"""
        self.config = EmailConfig()
        self.is_configured = bool(self.config.SENDGRID_API_KEY)

        if self.is_configured:
            logger.info(f"[OK] Email service configured (SendGrid)")
        else:
            logger.warning("[WARN] Email service not configured - set SENDGRID_API_KEY in .env")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str = None,
        text_content: str = None
    ) -> bool:
        """
        Gửi email qua SendGrid API

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
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            message = Mail(
                from_email=Email(self.config.FROM_EMAIL, self.config.FROM_NAME),
                to_emails=To(to_email),
                subject=subject
            )
            
            if html_content:
                message.add_content(Content("text/html", html_content))
            if text_content:
                message.add_content(Content("text/plain", text_content))
            
            sg = SendGridAPIClient(self.config.SENDGRID_API_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent to {to_email} (status: {response.status_code})")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except ImportError:
            logger.error("sendgrid package not installed. Run: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

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

    async def send_password_reset_email(self, email: str, full_name: str, reset_url: str) -> bool:
        """
        Gửi email đặt lại mật khẩu

        Args:
            email: Email người nhận
            full_name: Tên đầy đủ
            reset_url: URL đặt lại mật khẩu

        Returns:
            bool: True nếu gửi thành công
        """
        template = EmailTemplate.password_reset_email(full_name, email, reset_url)
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