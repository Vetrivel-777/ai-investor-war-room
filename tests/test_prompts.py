"""
Unit tests for the Prompts module (prompts.py).
Tests investor personas completeness, color values, avatars, and system prompt instructions.
"""

import pytest
from prompts import INVESTOR_PERSONAS, SYSTEM_INTERROGATION_PROMPT, SYSTEM_EVALUATION_PROMPT


class TestInvestorPersonas:
    def test_all_four_sharks_present(self):
        expected_sharks = ["market_shark", "tech_shark", "finance_shark", "skeptic_shark"]
        for s_id in expected_sharks:
            assert s_id in INVESTOR_PERSONAS

    def test_shark_persona_structure(self):
        required_keys = ["id", "name", "title", "focus", "tone", "avatar", "color"]
        for s_id, persona in INVESTOR_PERSONAS.items():
            for key in required_keys:
                assert key in persona, f"Persona {s_id} missing key '{key}'"
            assert isinstance(persona["focus"], list)
            assert len(persona["focus"]) >= 3
            assert persona["avatar"].strip() != ""
            assert persona["color"].startswith("#")

    def test_distinct_shark_roles(self):
        names = [p["name"] for p in INVESTOR_PERSONAS.values()]
        assert len(names) == len(set(names)), "Investor names must be unique"


class TestSystemPrompts:
    def test_interrogation_prompt_contains_critical_instructions(self):
        prompt = SYSTEM_INTERROGATION_PROMPT
        assert "TRUE CONTRADICTION" in prompt
        assert "STRATEGIC REFINEMENT" in prompt
        assert "ACKNOWLEDGED WEAKNESS" in prompt or "INTELLECTUAL HONESTY" in prompt
        assert "contradiction_warning" in prompt
        assert "next_shark_id" in prompt

    def test_evaluation_prompt_contains_scoring_guidelines(self):
        prompt = SYSTEM_EVALUATION_PROMPT
        assert "DISTINGUISH STRATEGIC REFINEMENTS FROM CONTRADICTIONS" in prompt
        assert "REWARD INTELLECTUAL HONESTY" in prompt
        assert "PENALIZE TRUE CONTRADICTIONS ONLY" in prompt
        assert "overall_score" in prompt
        assert "shark_verdicts" in prompt
        assert "INVEST" in prompt
        assert "INVEST WITH CONDITIONS" in prompt
        assert "PASS" in prompt
