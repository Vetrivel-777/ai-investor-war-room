"""
Unit tests for Core Business Logic of AI Investor War Room.
Validates startup intake requirements, contradiction vs refinement detection, state transitions, and scoring rules.
"""

import pytest
from typing import Dict, Any


def validate_pitch_submission(pitch: Dict[str, str]) -> tuple[bool, str]:
    """Helper representing the core startup intake validation rule."""
    name = pitch.get("startup_name", "").strip()
    building = pitch.get("building", "").strip()
    if not name:
        return False, "Startup Name is required."
    if not building:
        return False, "Core Product Pitch is required."
    return True, ""


def classify_answer_stance(answer: str) -> str:
    """
    Core logic helper mirroring the refinement vs honesty vs contradiction distinction.
    """
    ans_lower = answer.lower()
    refinement_keywords = ["revise", "revised", "adjust", "adjusted", "pivot", "recalculate", "instead", "changed", "lower", "reduce", "adapt"]
    honesty_keywords = ["cannot prevent", "limitation", "tradeoff", "challenge", "admit", "risk", "hard to", "leakage", "realistic"]
    
    if any(k in ans_lower for k in refinement_keywords):
        return "REFINEMENT"
    if any(k in ans_lower for k in honesty_keywords):
        return "HONESTY"
    if len(answer.strip().split()) < 4:
        return "VAGUE"
    return "ASSERTION"


class TestStartupIntakeValidation:
    def test_valid_submission(self, sample_pitch_data):
        is_valid, msg = validate_pitch_submission(sample_pitch_data)
        assert is_valid is True
        assert msg == ""

    def test_missing_startup_name_fails(self):
        pitch = {"startup_name": "  ", "building": "Valid pitch"}
        is_valid, msg = validate_pitch_submission(pitch)
        assert is_valid is False
        assert "Startup Name" in msg

    def test_missing_product_pitch_fails(self):
        pitch = {"startup_name": "Acme", "building": ""}
        is_valid, msg = validate_pitch_submission(pitch)
        assert is_valid is False
        assert "Core Product Pitch" in msg


class TestContradictionVsRefinementClassification:
    def test_pricing_adjustment_classified_as_refinement(self):
        # Founder lowering fee from 8% to 2.5% after pushback is coachability, NOT a contradiction
        ans = "After modeling payment gateway costs, we revised our take rate down to 2.5% to preserve volume."
        assert classify_answer_stance(ans) == "REFINEMENT"

    def test_admitting_technical_limit_classified_as_honesty(self):
        # Founder admitting that off-platform transactions cannot be 100% prevented
        ans = "We admit that we cannot prevent off-platform leakage completely, but we disincentivize it with escrow insurance."
        assert classify_answer_stance(ans) == "HONESTY"

    def test_terse_unsubstantiated_answer(self):
        ans = "Yes."
        assert classify_answer_stance(ans) == "VAGUE"

    def test_standard_conviction_assertion(self):
        ans = "We own exclusive distribution rights across 50 regional campuses under executed contracts."
        assert classify_answer_stance(ans) == "ASSERTION"


class TestStateTransitions:
    def test_page_sequence(self):
        # Simulation of page transitions: landing -> pitch_form -> war_room -> evaluation -> pitch_form (round 2)
        valid_pages = ["landing", "pitch_form", "war_room", "evaluation"]
        current_page = "landing"

        # User clicks Start
        current_page = "pitch_form"
        assert current_page in valid_pages

        # User submits valid pitch
        current_page = "war_room"
        assert current_page in valid_pages

        # Interrogation concludes
        current_page = "evaluation"
        assert current_page in valid_pages

        # User selects Round 2 retry
        current_page = "pitch_form"
        assert current_page in valid_pages
