"""
Shared pytest fixtures and test doubles for AI Investor War Room.
"""

import pytest
from typing import Dict, Any, List


@pytest.fixture
def sample_pitch_data() -> Dict[str, str]:
    """Provides a realistic sample startup pitch memo."""
    return {
        "startup_name": "NexusMetrics",
        "building": "AI-powered real-time cohort retention and telemetry platform for B2B SaaS.",
        "problem": "B2B SaaS companies lose 25% of annual revenue to silent customer churn because legacy analytics lack proactive predictive alerts.",
        "target_customer": "Mid-market B2B SaaS Chief Revenue Officers and Customer Success VPs.",
        "business_model": "Usage-based tiered subscription at $1,200/month average contract value with 85% gross margins."
    }


@pytest.fixture
def minimal_pitch_data() -> Dict[str, str]:
    """Provides a minimal valid pitch memo."""
    return {
        "startup_name": "QuickPay",
        "building": "Instant checkout widget for Shopify merchants.",
        "problem": "High cart abandonment at checkout.",
        "target_customer": "E-commerce merchants",
        "business_model": "1.5% transaction take-rate"
    }


@pytest.fixture
def sample_interrogation_turn() -> Dict[str, Any]:
    """Provides a single turn of interrogation."""
    return {
        "shark_id": "market_shark",
        "shark_name": "Market Shark",
        "question": "How specifically do you acquire mid-market customers without a bloated direct sales force?",
        "answer": "We drive organic inbound via free open-source database connectors and product-led growth onboarding."
    }


@pytest.fixture
def sample_interrogation_history(sample_pitch_data) -> List[Dict[str, Any]]:
    """Provides a multi-turn interrogation transcript spanning all sharks."""
    return [
        {
            "shark_id": "market_shark",
            "shark_name": "Market Shark",
            "question": "What is your customer acquisition cost (CAC) and tested sales channel?",
            "answer": "We rely on developer-led organic distribution; current CAC is $450 with 4-month payback."
        },
        {
            "shark_id": "tech_shark",
            "shark_name": "Tech Shark",
            "question": "What prevents Snowflake or Datadog from building this as a feature next quarter?",
            "answer": "We have proprietary streaming anomaly detection and patent-pending temporal graph indexes that reduce query latency 10x."
        },
        {
            "shark_id": "finance_shark",
            "shark_name": "Finance Shark",
            "question": "Explain your gross margin structure when cloud egress costs scale with customer data volume.",
            "answer": "We revised our pricing to pass through high-volume egress costs, ensuring our gross margin remains above 80%."
        },
        {
            "shark_id": "skeptic_shark",
            "shark_name": "Skeptic Shark",
            "question": "What is your single biggest point of failure in the next 12 months?",
            "answer": "We admit that enterprise compliance certifications like SOC2 Type II are our main bottleneck to closing Fortune 500 pilots."
        }
    ]


@pytest.fixture
def raw_evaluation_json() -> Dict[str, Any]:
    """Provides a sample raw evaluation dictionary returned by AI Engine."""
    return {
        "overall_score": 82,
        "subscores": {
            "problem": 88,
            "market": 84,
            "technology": 82,
            "business_model": 80,
            "competition": 78,
            "defensibility": 80
        },
        "shark_verdicts": {
            "Market Shark": "INVEST - Clear product-led distribution model with strong early retention metrics.",
            "Tech Shark": "INVEST WITH CONDITIONS - Scalability architecture is defensible but requires stress testing at petabyte volume.",
            "Finance Shark": "INVEST - Pass-through pricing preserves attractive unit margins.",
            "Skeptic Shark": "INVEST WITH CONDITIONS - SOC2 certification timeline poses minor enterprise sales lag."
        },
        "biggest_strength": "High-velocity product-led growth distribution and clear founder coachability.",
        "biggest_weakness": "Enterprise sales cycle friction due to uncompleted compliance audits.",
        "biggest_concern": "Incumbent telemetry platforms rolling out competing basic cohort dashboards.",
        "top_improvements": [
            "Accelerate SOC2 Type II certification to unlock enterprise enterprise pipelines.",
            "Formalize design partner pilot contracts into binding multi-year agreements.",
            "Demonstrate net revenue retention (NRR) exceeding 120%."
        ],
        "final_decision": "INVEST WITH CONDITIONS",
        "is_fallback": False
    }
