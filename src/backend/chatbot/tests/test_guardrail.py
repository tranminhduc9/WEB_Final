"""
Test Guardrail Node

Tests for the guardrail_node which checks:
- Profanity (Vietnamese/English)
- PII (Phone numbers, Emails)

This test uses ALGORITHMIC checks only, no LLM calls.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from chatbot.utils import is_safe_query, check_profanity, check_pii


class TestGuardrailProfanity:
    """Test profanity detection."""
    
    def test_clean_query_passes(self):
        """Clean query should pass guardrail."""
        is_safe, message = is_safe_query("Cho tôi biết về Hồ Hoàn Kiếm")
        assert is_safe is True
        assert message == ""
        print("✅ Clean query passed")
    
    def test_vietnamese_profanity_detected(self):
        """Vietnamese profanity should be detected."""
        has_profanity, violations = check_profanity("dit me may")
        assert has_profanity is True
        print(f"✅ Vietnamese profanity detected: {violations}")
    
    def test_english_profanity_detected(self):
        """English profanity should be detected."""
        has_profanity, violations = check_profanity("what the fuck")
        assert has_profanity is True
        print(f"✅ English profanity detected: {violations}")
    
    def test_mixed_profanity_detected(self):
        """Mixed language profanity should be detected."""
        has_profanity, violations = check_profanity("vcl sao shit thế")
        assert has_profanity is True
        print(f"✅ Mixed profanity detected: {violations}")
    
    def test_profanity_guardrail_rejection(self):
        """Profanity should trigger guardrail rejection."""
        is_safe, message = is_safe_query("dm thằng ngu")
        assert is_safe is False
        assert "ngôn ngữ không phù hợp" in message
        print(f"✅ Profanity rejected with message: {message[:50]}...")


class TestGuardrailPII:
    """Test PII detection."""
    
    def test_phone_number_detected(self):
        """Phone numbers should be detected."""
        has_pii, types = check_pii("Gọi tôi số 0912345678")
        assert has_pii is True
        assert "phone_number" in types
        print(f"✅ Phone number detected: {types}")
    
    def test_phone_with_country_code(self):
        """Phone with +84 country code should be detected."""
        has_pii, types = check_pii("Số điện thoại: +84 912345678")
        assert has_pii is True
        assert "phone_number" in types
        print(f"✅ Phone with +84 detected: {types}")
    
    def test_email_detected(self):
        """Email addresses should be detected."""
        has_pii, types = check_pii("Email của tôi là test@example.com")
        assert has_pii is True
        assert "email" in types
        print(f"✅ Email detected: {types}")
    
    def test_pii_guardrail_rejection(self):
        """PII should trigger guardrail rejection."""
        is_safe, message = is_safe_query("Số điện thoại tôi là 0987654321")
        assert is_safe is False
        assert "thông tin cá nhân" in message or "bảo mật" in message
        print(f"✅ PII rejected with message: {message[:50]}...")
    
    def test_no_pii_in_clean_text(self):
        """Clean text should not trigger PII detection."""
        has_pii, types = check_pii("Hà Nội có rất nhiều địa điểm đẹp")
        assert has_pii is False
        print("✅ No PII in clean text")


class TestGuardrailIntegration:
    """Integration tests for guardrail."""
    
    def test_multiple_violations(self):
        """Multiple violations should all be caught."""
        # Profanity + phone
        is_safe, message = is_safe_query("dm gọi tôi 0912345678")
        assert is_safe is False
        print(f"✅ Multiple violations detected: {message[:50]}...")
    
    def test_edge_cases(self):
        """Edge cases should be handled."""
        # Empty string - safe
        is_safe, _ = is_safe_query("")
        assert is_safe is True
        
        # Just whitespace - safe
        is_safe, _ = is_safe_query("   ")
        assert is_safe is True
        
        # Price in VND (avoid "dong" word which may trigger false positive)
        is_safe, _ = is_safe_query("Giá là 50000 VND")
        assert is_safe is True
        
        # Normal numbers - safe
        is_safe, _ = is_safe_query("Có 5 địa điểm du lịch")
        assert is_safe is True
        
        print("✅ Edge cases handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
