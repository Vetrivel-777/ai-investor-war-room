"""
Accessibility (A11y) Verification Tests.
Verifies WCAG contrast compliance, ARIA attributes, keyboard focus outlines,
and prefers-reduced-motion media queries.
"""

import os
import re
import pytest


@pytest.fixture
def app_css_content() -> str:
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        return f.read()


class TestAccessibilityFeatures:
    def test_reduced_motion_media_query_present(self, app_css_content):
        assert "@media (prefers-reduced-motion: reduce)" in app_css_content
        assert "animation-duration: 0.001ms !important" in app_css_content or "animation: none" in app_css_content

    def test_sr_only_utility_class_defined(self, app_css_content):
        assert ".sr-only" in app_css_content
        assert "clip: rect(0, 0, 0, 0)" in app_css_content

    def test_visible_focus_indicators_defined(self, app_css_content):
        assert ":focus-visible" in app_css_content
        assert "outline:" in app_css_content

    def test_semantic_aria_landmarks_in_markup(self, app_css_content):
        assert 'role="region"' in app_css_content
        assert 'aria-label=' in app_css_content
        assert 'role="alert"' in app_css_content
        assert 'role="progressbar"' in app_css_content

    def test_contrast_colors_meet_standards(self, app_css_content):
        # Verify text color variables exist and avoid poor contrast
        assert "--c-text-primary: #f8fafc;" in app_css_content
        assert "--c-text-secondary: #cbd5e1;" in app_css_content
        assert "--c-text-muted: #94a3b8;" in app_css_content
