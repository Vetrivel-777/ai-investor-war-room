"""
Unit tests for the Evaluator module (evaluator.py).
Tests scorecard parsing, score bounds enforcement, decision sentiment, and comparative Round 2 delta analysis.
"""

import pytest
from evaluator import (
    PitchScorecard,
    parse_scorecard_json,
    clamp_score,
    compare_scorecards,
    DIMENSION_KEYS
)


class TestEvaluatorParsing:
    def test_parse_valid_scorecard(self, raw_evaluation_json):
        card = parse_scorecard_json(raw_evaluation_json)
        assert isinstance(card, PitchScorecard)
        assert card.overall_score == 82
        assert card.final_decision == "INVEST WITH CONDITIONS"
        assert card.is_fallback is False
        assert len(card.subscores) == 6
        for dim in DIMENSION_KEYS:
            assert dim in card.subscores

    def test_parse_empty_dict_uses_safe_fallbacks(self):
        card = parse_scorecard_json({})
        assert isinstance(card, PitchScorecard)
        assert 0 <= card.overall_score <= 100
        assert card.final_decision in ("INVEST", "INVEST WITH CONDITIONS", "PASS")
        assert len(card.subscores) == 6
        assert len(card.shark_verdicts) == 4
        assert len(card.top_improvements) > 0

    def test_score_clamping_limits(self):
        # Out-of-bounds scores must be clamped to 0..100
        raw = {
            "overall_score": 150,
            "subscores": {
                "problem": 120,
                "market": -45,
                "technology": 999,
                "business_model": "invalid",
                "competition": 70,
                "defensibility": 50
            }
        }
        card = parse_scorecard_json(raw)
        assert card.overall_score == 100
        assert card.subscores["problem"] == 100
        assert card.subscores["market"] == 0
        assert card.subscores["technology"] == 100
        assert card.subscores["business_model"] == 70  # default fallback for invalid string

    def test_is_investment_approved_method(self):
        invest_card = parse_scorecard_json({"final_decision": "INVEST"})
        assert invest_card.is_investment_approved() is True

        cond_card = parse_scorecard_json({"final_decision": "INVEST WITH CONDITIONS"})
        assert cond_card.is_investment_approved() is True

        pass_card = parse_scorecard_json({"final_decision": "PASS"})
        assert pass_card.is_investment_approved() is False

    def test_decision_sentiment_method(self):
        invest_card = parse_scorecard_json({"final_decision": "INVEST"})
        assert invest_card.get_decision_sentiment() == "positive"

        cond_card = parse_scorecard_json({"final_decision": "INVEST WITH CONDITIONS"})
        assert cond_card.get_decision_sentiment() == "caution"

        pass_card = parse_scorecard_json({"final_decision": "PASS"})
        assert pass_card.get_decision_sentiment() == "negative"


class TestScorecardComparison:
    def test_compare_scorecards_improvement(self):
        round1 = parse_scorecard_json({
            "overall_score": 68,
            "subscores": {"problem": 70, "market": 65, "technology": 65, "business_model": 65, "competition": 60, "defensibility": 60},
            "final_decision": "PASS"
        })
        round2 = parse_scorecard_json({
            "overall_score": 82,
            "subscores": {"problem": 85, "market": 80, "technology": 80, "business_model": 80, "competition": 75, "defensibility": 75},
            "final_decision": "INVEST WITH CONDITIONS"
        })

        comp = compare_scorecards(round1, round2)
        assert comp["overall_delta"] == 14
        assert comp["trajectory"] == "IMPROVED"
        assert comp["improved_count"] == 6
        assert comp["regressed_count"] == 0
        assert comp["decision_changed"] is True
        assert comp["previous_decision"] == "PASS"
        assert comp["current_decision"] == "INVEST WITH CONDITIONS"

    def test_compare_scorecards_decline(self):
        round1 = parse_scorecard_json({"overall_score": 80})
        round2 = parse_scorecard_json({"overall_score": 72})

        comp = compare_scorecards(round1, round2)
        assert comp["overall_delta"] == -8
        assert comp["trajectory"] == "DECLINED"

    def test_compare_scorecards_steady(self):
        round1 = parse_scorecard_json({"overall_score": 75})
        round2 = parse_scorecard_json({"overall_score": 75})

        comp = compare_scorecards(round1, round2)
        assert comp["overall_delta"] == 0
        assert comp["trajectory"] == "MAINTAINED"
