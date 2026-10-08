"""
Security and Defensive Engineering Tests.
Tests HTML escaping against XSS vectors, secret redaction, and environment isolation.
"""

import os
import re
import pytest
from app import esc
from ai_engine import _safe_log_error, get_api_key


class TestXssSanitization:
    def test_escapes_script_tags(self):
        malicious = "<script>alert('xss')</script>"
        sanitized = esc(malicious)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized

    def test_escapes_event_handlers_and_quotes(self):
        payload = '"><img src=x onerror=alert(1)>'
        sanitized = esc(payload)
        assert '"><' not in sanitized
        assert "&quot;&gt;&lt;img" in sanitized

    def test_handles_none_and_numbers(self):
        assert esc(None) == ""
        assert esc(42) == "42"


class TestSecretSanitization:
    def test_safe_log_error_redacts_tokens(self, capsys):
        err = Exception("Failed request to https://api.example.com?key=AIzaSySecretKey123&token=tok_998877")
        _safe_log_error("TestPrefix", err)
        captured = capsys.readouterr().out
        assert "AIzaSySecretKey123" not in captured
        assert "[REDACTED]" in captured

    def test_gitignore_protects_env_files(self):
        gitignore_path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        assert os.path.exists(gitignore_path)
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".env" in content
        assert ".streamlit/secrets.toml" in content

    def test_no_hardcoded_api_keys_in_source_code(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        source_files = ["app.py", "ai_engine.py", "evaluator.py", "prompts.py"]
        # Common Google API key pattern: AIzaSy[A-Za-z0-9_-]{33}
        api_key_pattern = re.compile(r"AIzaSy[A-Za-z0-9_\-]{33}")

        for fname in source_files:
            fpath = os.path.join(project_root, fname)
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                matches = api_key_pattern.findall(content)
                assert len(matches) == 0, f"Found hardcoded API key in {fname}: {matches}"
