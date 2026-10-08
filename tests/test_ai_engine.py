"""
Unit tests for AI Engine module (ai_engine.py).
Tests fallback question generation, fallback scorecard evaluation, response parsing,
transient error detection, and mock client behavior.
"""

import pytest
from unittest.mock import MagicMock, patch
from ai_engine import (
    get_api_key,
    _clean_json_response,
    _is_transient_error,
    format_pitch_memo,
    format_transcript,
    get_fallback_first_question,
    get_fallback_next_question,
    get_fallback_evaluation,
    generate_first_question,
    generate_next_adaptive_question,
    generate_final_evaluation,
    FALLBACK_QUESTIONS
)


class TestJsonCleaning:
    def test_clean_standard_json(self):
        raw = '{"question": "How do you scale?", "next_shark_id": "tech_shark"}'
        parsed = _clean_json_response(raw)
        assert parsed["next_shark_id"] == "tech_shark"
        assert parsed["question"] == "How do you scale?"

    def test_clean_markdown_fenced_json(self):
        raw = """```json
{
    "question": "What is your gross margin?",
    "next_shark_id": "finance_shark",
    "contradiction_warning": null
}
```"""
        parsed = _clean_json_response(raw)
        assert parsed["next_shark_id"] == "finance_shark"

    def test_clean_json_with_preamble(self):
        raw = """Here is the investor question:
{"question": "Explain your TAM calculation.", "next_shark_id": "market_shark"}
Thank you!"""
        parsed = _clean_json_response(raw)
        assert parsed["next_shark_id"] == "market_shark"


class TestTransientErrorDetection:
    def test_identifies_503_and_rate_limits(self):
        assert _is_transient_error(Exception("503 Service Unavailable")) is True
        assert _is_transient_error(Exception("RESOURCE_EXHAUSTED 429")) is True
        assert _is_transient_error(Exception("Server overloaded, try again")) is True

    def test_identifies_non_transient_errors(self):
        assert _is_transient_error(Exception("Invalid API key provided")) is False
        assert _is_transient_error(Exception("404 Not Found")) is False


class TestFallbackEngine:
    def test_fallback_first_question_structure(self, sample_pitch_data):
        q = get_fallback_first_question(sample_pitch_data)
        assert q["shark_id"] == "market_shark"
        assert q["is_fallback"] is True
        assert sample_pitch_data["startup_name"] in q["question"] or "NexusMetrics" in q["question"]

    def test_fallback_next_question_rotates_sharks(self, sample_pitch_data):
        history = [
            {"shark_id": "market_shark", "shark_name": "Market Shark", "question": "Q1", "answer": "Answer 1"}
        ]
        q = get_fallback_next_question(sample_pitch_data, history)
        assert q["shark_id"] != "market_shark"
        assert q["is_fallback"] is True

    def test_fallback_detects_refinement_without_false_contradiction(self, sample_pitch_data):
        history = [
            {
                "shark_id": "finance_shark",
                "shark_name": "Finance Shark",
                "question": "What is your fee?",
                "answer": "We revised our pricing down to 2% to better serve SMBs."
            }
        ]
        q = get_fallback_next_question(sample_pitch_data, history)
        assert q["contradiction_warning"] is None

    def test_fallback_evaluation_produces_complete_scorecard(self, sample_pitch_data, sample_interrogation_history):
        res = get_fallback_evaluation(sample_pitch_data, sample_interrogation_history)
        assert 0 <= res["overall_score"] <= 100
        assert len(res["subscores"]) == 6
        assert len(res["shark_verdicts"]) == 4
        assert len(res["top_improvements"]) == 3
        assert res["final_decision"] in ("INVEST", "INVEST WITH CONDITIONS", "PASS")
        assert res["is_fallback"] is True


class TestFormatHelpers:
    def test_format_pitch_memo(self, sample_pitch_data):
        memo = format_pitch_memo(sample_pitch_data)
        assert "NexusMetrics" in memo
        assert "STARTUP PITCH MEMO:" in memo

    def test_format_transcript(self, sample_interrogation_history):
        transcript = format_transcript(sample_interrogation_history)
        assert "Turn 1" in transcript
        assert "Turn 2" in transcript
        assert "Market Shark" in transcript


class TestMockGeminiInteractions:
    @patch("ai_engine.get_genai_client")
    def test_generate_first_question_success(self, mock_get_client, sample_pitch_data):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"next_shark_id": "tech_shark", "question": "Can your architecture scale?", "contradiction_warning": null}'
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        q = generate_first_question(sample_pitch_data)
        assert q["shark_id"] == "tech_shark"
        assert q["is_fallback"] is False
        assert "Can your architecture scale?" in q["question"]

    @patch("time.sleep", return_value=None)
    @patch("ai_engine.get_genai_client")
    def test_generate_first_question_graceful_fallback_on_api_error(self, mock_get_client, mock_sleep, sample_pitch_data):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API unavailable")
        mock_get_client.return_value = mock_client

        q = generate_first_question(sample_pitch_data)
        assert q["is_fallback"] is True
        assert q["shark_id"] in ("market_shark", "tech_shark", "finance_shark", "skeptic_shark")
