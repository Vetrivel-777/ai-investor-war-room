"""
End-to-End Simulation Test for AI Investor War Room.
Simulates a complete founder lifecycle through the simulator:
1. Startup Pitch Memo Submission
2. Panel opens interrogation (Market Shark)
3. Founder answers with strategic refinement
4. Adaptive follow-up from Tech Shark
5. Founder answers with intellectual honesty
6. Deliberation & Scorecard generation
7. Round 2 re-pitch with improved answers
8. Comparative growth delta calculation
"""

import pytest
from ai_engine import (
    get_fallback_first_question,
    get_fallback_next_question,
    get_fallback_evaluation
)
from evaluator import parse_scorecard_json, compare_scorecards


class TestEndToEndSimulation:
    def test_complete_founder_war_room_journey(self, sample_pitch_data):
        # STEP 1: Founder submits Pitch Memo
        pitch = dict(sample_pitch_data)
        assert len(pitch["startup_name"]) > 0
        assert len(pitch["building"]) > 0

        # STEP 2: Panel initiates first challenge
        q1 = get_fallback_first_question(pitch)
        assert q1["shark_id"] == "market_shark"
        assert len(q1["question"]) > 0

        # STEP 3: Founder responds with strategic pricing refinement
        interrogation_history = []
        interrogation_history.append({
            "shark_id": q1["shark_id"],
            "shark_name": q1["shark_name"],
            "question": q1["question"],
            "answer": "We revised our initial unit pricing to $800/mo to accelerate initial velocity, maintaining 82% gross margins."
        })

        # STEP 4: Next adaptive question generated (Rotates to Tech Shark)
        q2 = get_fallback_next_question(pitch, interrogation_history)
        assert q2["shark_id"] in ("tech_shark", "finance_shark", "skeptic_shark")
        # Ensure strategic refinement was NOT misclassified as a contradiction
        assert q2["contradiction_warning"] is None

        # STEP 5: Founder responds with technical honesty regarding operational limits
        interrogation_history.append({
            "shark_id": q2["shark_id"],
            "shark_name": q2["shark_name"],
            "question": q2["question"],
            "answer": "We acknowledge our limitation in edge computing environments; our patent-pending indexing runs cloud-native on Kubernetes."
        })

        # STEP 6: Next adaptive question generated
        q3 = get_fallback_next_question(pitch, interrogation_history)
        assert q3["contradiction_warning"] is None

        interrogation_history.append({
            "shark_id": q3["shark_id"],
            "shark_name": q3["shark_name"],
            "question": q3["question"],
            "answer": "Our CAC payback is 4.5 months with 135% net revenue retention from early cohort customers."
        })

        # STEP 7: Conclude Interrogation and assemble Round 1 Scorecard
        raw_eval_round1 = get_fallback_evaluation(pitch, interrogation_history)
        round1_card = parse_scorecard_json(raw_eval_round1)

        assert 0 <= round1_card.overall_score <= 100
        assert len(round1_card.subscores) == 6
        assert round1_card.final_decision in ("INVEST", "INVEST WITH CONDITIONS", "PASS")

        # STEP 8: Round 2 Re-pitching Simulation
        # Founder refines pitch and provides even stronger answers with concrete moats
        refined_pitch = dict(pitch)
        refined_pitch["problem"] += " Validated with 14 signed letters of intent representing $320k pipeline."

        round2_history = list(interrogation_history)
        round2_history.append({
            "shark_id": "skeptic_shark",
            "shark_name": "Skeptic Shark",
            "question": "What happens if competitors clone this in 6 months?",
            "answer": "We have an exclusive proprietary dataset and multi-tenant telemetry network effects creating irreversible customer switching costs."
        })

        raw_eval_round2 = get_fallback_evaluation(refined_pitch, round2_history)
        round2_card = parse_scorecard_json(raw_eval_round2)

        # STEP 9: Compare Round 1 vs Round 2 Analytics
        comparison = compare_scorecards(round1_card, round2_card)
        assert "overall_delta" in comparison
        assert "trajectory" in comparison
        assert "summary_statement" in comparison
        assert comparison["trajectory"] in ("IMPROVED", "MAINTAINED", "DECLINED")
