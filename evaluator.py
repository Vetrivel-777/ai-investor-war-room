"""
Evaluator module for AI Investor War Room.
Processes pitch performance, enforces score bounds, and structures scorecard comparison.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

__all__ = [
    "PitchScorecard",
    "parse_scorecard_json",
    "compare_scorecards",
    "clamp_score",
    "DIMENSION_KEYS",
    "DIMENSION_LABELS",
]

DIMENSION_KEYS = [
    "problem",
    "market",
    "technology",
    "business_model",
    "competition",
    "defensibility",
]

DIMENSION_LABELS = {
    "problem": "Problem Validation",
    "market": "Market & TAM",
    "technology": "Technology & Moat",
    "business_model": "Unit Economics",
    "competition": "Competition Defense",
    "defensibility": "Defensibility",
}


@dataclass
class PitchScorecard:
    overall_score: int
    subscores: Dict[str, int]
    shark_verdicts: Dict[str, str]
    biggest_strength: str
    biggest_weakness: str
    biggest_concern: str
    top_improvements: List[str]
    final_decision: str  # INVEST, INVEST WITH CONDITIONS, PASS
    is_fallback: bool = False

    def is_investment_approved(self) -> bool:
        """Returns True if the syndicate decided to invest (full or with conditions)."""
        return self.final_decision in ("INVEST", "INVEST WITH CONDITIONS")

    def get_decision_sentiment(self) -> str:
        """Returns positive, neutral, or negative sentiment for accessible styling."""
        if self.final_decision == "INVEST":
            return "positive"
        elif self.final_decision == "INVEST WITH CONDITIONS":
            return "caution"
        return "negative"


def clamp_score(value: Any, default: int = 70, min_val: int = 0, max_val: int = 100) -> int:
    """Safely coerces and clamps a numerical score within valid boundaries."""
    try:
        val = int(value)
        return max(min_val, min(max_val, val))
    except (TypeError, ValueError):
        return default


def parse_scorecard_json(data: Dict[str, Any]) -> PitchScorecard:
    """Helper to convert dictionary JSON from AI Engine into typed, validated PitchScorecard."""
    raw_subscores = data.get("subscores", {})
    if not isinstance(raw_subscores, dict):
        raw_subscores = {}

    validated_subscores = {
        "problem": clamp_score(raw_subscores.get("problem", 75)),
        "market": clamp_score(raw_subscores.get("market", 70)),
        "technology": clamp_score(raw_subscores.get("technology", 70)),
        "business_model": clamp_score(raw_subscores.get("business_model", 70)),
        "competition": clamp_score(raw_subscores.get("competition", 65)),
        "defensibility": clamp_score(raw_subscores.get("defensibility", 65)),
    }

    raw_overall = data.get("overall_score")
    if raw_overall is not None:
        overall_score = clamp_score(raw_overall, 75)
    else:
        # Compute mean of subscores if overall is omitted
        overall_score = int(sum(validated_subscores.values()) / len(validated_subscores))

    # Validate decision string
    decision = str(data.get("final_decision", "INVEST WITH CONDITIONS")).strip().upper()
    if decision not in ("INVEST", "INVEST WITH CONDITIONS", "PASS"):
        if overall_score >= 85:
            decision = "INVEST"
        elif overall_score >= 70:
            decision = "INVEST WITH CONDITIONS"
        else:
            decision = "PASS"

    # Default shark verdicts if missing or non-dict
    raw_verdicts = data.get("shark_verdicts")
    if not isinstance(raw_verdicts, dict) or not raw_verdicts:
        raw_verdicts = {
            "Market Shark": "INVEST WITH CONDITIONS - Demand is plausible but CAC needs proof",
            "Tech Shark": "INVEST WITH CONDITIONS - Scalability requires architectural roadmap",
            "Finance Shark": "PASS - Margin targets are optimistic",
            "Skeptic Shark": "PASS - High risk of competitive replication"
        }

    raw_improvements = data.get("top_improvements")
    if not isinstance(raw_improvements, list) or not raw_improvements:
        raw_improvements = [
            "Validate customer willingness to pay via paid LOIs",
            "Define defensible technical or data flywheel mechanisms",
            "Establish unit economic payback under 6 months"
        ]

    return PitchScorecard(
        overall_score=overall_score,
        subscores=validated_subscores,
        shark_verdicts={str(k): str(v) for k, v in raw_verdicts.items()},
        biggest_strength=str(data.get("biggest_strength", "Clear initial problem identification")),
        biggest_weakness=str(data.get("biggest_weakness", "Unproven long-term competitive moat")),
        biggest_concern=str(data.get("biggest_concern", "Incumbents offering similar capability at zero marginal cost")),
        top_improvements=[str(item) for item in raw_improvements],
        final_decision=decision,
        is_fallback=bool(data.get("is_fallback", False))
    )


def compare_scorecards(previous: PitchScorecard, current: PitchScorecard) -> Dict[str, Any]:
    """
    Computes delta and improvement analytics between Round 1 and Round 2 scorecards.
    Returns comprehensive metrics for comparative analysis.
    """
    overall_delta = current.overall_score - previous.overall_score

    subscore_deltas = {}
    improved_dimensions = []
    regressed_dimensions = []

    for dim in DIMENSION_KEYS:
        prev_val = previous.subscores.get(dim, 70)
        curr_val = current.subscores.get(dim, 70)
        delta = curr_val - prev_val
        subscore_deltas[dim] = delta
        if delta > 0:
            improved_dimensions.append(DIMENSION_LABELS.get(dim, dim))
        elif delta < 0:
            regressed_dimensions.append(DIMENSION_LABELS.get(dim, dim))

    if overall_delta > 0:
        trajectory = "IMPROVED"
        summary_statement = f"Venture score improved by +{overall_delta} points following strategic adjustments."
    elif overall_delta < 0:
        trajectory = "DECLINED"
        summary_statement = f"Venture score declined by {overall_delta} points under subsequent stress testing."
    else:
        trajectory = "MAINTAINED"
        summary_statement = "Venture score held steady between rounds."

    return {
        "overall_delta": overall_delta,
        "subscore_deltas": subscore_deltas,
        "trajectory": trajectory,
        "summary_statement": summary_statement,
        "improved_count": len(improved_dimensions),
        "regressed_count": len(regressed_dimensions),
        "improved_dimensions": improved_dimensions,
        "regressed_dimensions": regressed_dimensions,
        "previous_decision": previous.final_decision,
        "current_decision": current.final_decision,
        "decision_changed": previous.final_decision != current.final_decision,
    }
