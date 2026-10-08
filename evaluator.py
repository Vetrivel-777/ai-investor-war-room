"""
Evaluator module for AI Investor War Room.
Processes pitch performance and structures the final scorecard presentation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

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

def parse_scorecard_json(data: Dict[str, Any]) -> PitchScorecard:
    """Helper to convert dictionary JSON from AI Engine into typed PitchScorecard."""
    subscores = data.get("subscores", {})
    default_subscores = {
        "problem": subscores.get("problem", 75),
        "market": subscores.get("market", 70),
        "technology": subscores.get("technology", 70),
        "business_model": subscores.get("business_model", 70),
        "competition": subscores.get("competition", 65),
        "defensibility": subscores.get("defensibility", 65),
    }

    return PitchScorecard(
        overall_score=int(data.get("overall_score", 75)),
        subscores=default_subscores,
        shark_verdicts=data.get("shark_verdicts", {
            "Market Shark": "INVEST WITH CONDITIONS - Demand is plausible but CAC needs proof",
            "Tech Shark": "INVEST WITH CONDITIONS - Scalability requires architectural roadmap",
            "Finance Shark": "PASS - Margin targets are optimistic",
            "Skeptic Shark": "PASS - High risk of competitive replication"
        }),
        biggest_strength=data.get("biggest_strength", "Clear initial problem identification"),
        biggest_weakness=data.get("biggest_weakness", "Unproven long-term competitive moat"),
        biggest_concern=data.get("biggest_concern", "Incumbents offering similar capability at zero marginal cost"),
        top_improvements=data.get("top_improvements", [
            "Validate customer willingness to pay via paid LOIs",
            "Define defensible technical or data flywheel mechanisms",
            "Establish unit economic payback under 6 months"
        ]),
        final_decision=data.get("final_decision", "INVEST WITH CONDITIONS"),
        is_fallback=bool(data.get("is_fallback", False))
    )
