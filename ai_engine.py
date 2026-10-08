"""
AI Engine module for AI Investor War Room.
Integrates with Google Gemini API via google-genai SDK for adaptive interrogation and pitch evaluation.
Includes bounded exponential backoff retries for transient 503/UNAVAILABLE errors and pitch-specific deterministic fallbacks.
"""

import os
import json
import re
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import SYSTEM_INTERROGATION_PROMPT, SYSTEM_EVALUATION_PROMPT, INVESTOR_PERSONAS

# Load environment variables from .env file
load_dotenv()

# Model configuration - primary model set to gemini-3.5-flash with supported fallback models
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Fallback sequence of supported Gemini Flash models
_candidate_models = [
    DEFAULT_MODEL,
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash"
]
# Deduplicate while preserving order
PREFERRED_MODELS: List[str] = []
for _m in _candidate_models:
    if _m and _m not in PREFERRED_MODELS:
        PREFERRED_MODELS.append(_m)


def get_api_key() -> Optional[str]:
    """Retrieve Gemini API Key from environment variables."""
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip() and key != "your_gemini_api_key_here":
        return key.strip()
    return None


def get_genai_client() -> Optional[genai.Client]:
    """Initialize and return google-genai Client if API key is present."""
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing GenAI Client: {e}")
        return None


def _clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Helper to extract and parse JSON from LLM response text."""
    text = raw_text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
    return json.loads(text)


def _is_transient_error(e: Exception) -> bool:
    """Check if exception is a transient server/rate limit/capacity error (503, 429, etc.)."""
    err_str = str(e).lower()
    transient_indicators = [
        "503", "unavailable", "high demand", "overloaded", "capacity",
        "429", "resource_exhausted", "quota", "rate limit", "timeout",
        "500", "502", "504", "server error"
    ]
    return any(indicator in err_str for indicator in transient_indicators)


def _call_gemini(client: genai.Client, prompt: str, system_instruction: str) -> str:
    """
    Invokes Gemini API with bounded exponential-backoff retry handling specifically
    for transient 503/UNAVAILABLE errors and automatic model fallback.
    """
    last_error = None
    max_retries_per_model = 3
    initial_delay = 1.0
    backoff_factor = 2.0
    max_delay = 6.0

    for model_name in PREFERRED_MODELS:
        delay = initial_delay
        for attempt in range(max_retries_per_model):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    response_mime_type="application/json"
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                if _is_transient_error(e) and attempt < max_retries_per_model - 1:
                    time.sleep(delay)
                    delay = min(max_delay, delay * backoff_factor)
                    continue
                else:
                    # Switch to next model on failure
                    break

    raise RuntimeError(f"Gemini API call failed across models: {last_error}")


# ---------------------------------------------------------
# DETERMINISTIC FALLBACK ENGINE
# ---------------------------------------------------------

FALLBACK_QUESTIONS = {
    "market_shark": [
        "How specifically do you plan to acquire your first 1,000 {target_customer} customers for {startup_name}, and what customer acquisition channels have you tested?",
        "Who are your top two direct competitors serving {target_customer}, and what is your clear go-to-market advantage over them?",
        "What is your total addressable market (TAM) estimate for {startup_name}, and how quickly can you capture initial market share?",
        "Why is now the right market timing for {startup_name}, and what industry shifts make customers urgently need {building}?"
    ],
    "tech_shark": [
        "What is the core technical architecture behind {startup_name}, and what prevents a competitor from cloning {building} in 3 months?",
        "How does your tech stack handle scalability when user traffic or data processing grows 100x?",
        "Do you rely on third-party APIs or proprietary models for {startup_name}, and how do you protect your technical IP?",
        "What is the single biggest technical bottleneck or operational single point of failure in your current product build?"
    ],
    "finance_shark": [
        "Walk me through your unit economics for {business_model}: what is your target gross margin and CAC payback period?",
        "What are the major cost drivers to deliver {building} at scale, and how do your margins improve over time?",
        "How much runway and funding does {startup_name} require to reach profitability under your current financial projections?",
        "What is your pricing strategy for {target_customer}, and have you validated customer willingness to pay?"
    ],
    "skeptic_shark": [
        "What is the single weakest assumption in your pitch memo for {startup_name} that could cause the business to fail?",
        "You claim to solve '{problem}', but why haven't well-funded incumbents already added this capability for free?",
        "If customer acquisition costs double and conversion rates drop by half, how does {startup_name} stay default alive?",
        "What specific metric or customer evidence proves that {target_customer} will pay recurring revenue for {building}?"
    ]
}


def get_fallback_first_question(pitch_data: Dict[str, str]) -> Dict[str, Any]:
    """Generates a pitch-specific opening question when Gemini is unavailable."""
    startup_name = pitch_data.get("startup_name") or "your startup"
    target_customer = pitch_data.get("target_customer") or "target customers"
    building = pitch_data.get("building") or "your product"
    problem = pitch_data.get("problem") or "the core problem"
    business_model = pitch_data.get("business_model") or "your pricing model"

    shark_id = "market_shark"
    q_template = FALLBACK_QUESTIONS["market_shark"][0]
    question = q_template.format(
        startup_name=startup_name,
        target_customer=target_customer,
        building=building,
        problem=problem,
        business_model=business_model
    )

    return {
        "shark_id": shark_id,
        "shark_name": INVESTOR_PERSONAS[shark_id]["name"],
        "contradiction_warning": None,
        "question": question,
        "is_fallback": True,
        "fallback_reason": "AI temporarily unavailable — using Investor Backup Question"
    }


def get_fallback_next_question(
    pitch_data: Dict[str, str],
    interrogation_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates an adaptive pitch-specific follow-up question when Gemini is unavailable."""
    startup_name = pitch_data.get("startup_name") or "your startup"
    target_customer = pitch_data.get("target_customer") or "target customers"
    building = pitch_data.get("building") or "your product"
    problem = pitch_data.get("problem") or "the core problem"
    business_model = pitch_data.get("business_model") or "your pricing model"

    shark_order = ["market_shark", "tech_shark", "finance_shark", "skeptic_shark"]
    counts = {s: 0 for s in shark_order}
    for turn in interrogation_history:
        s_id = turn.get("shark_id")
        if s_id in counts:
            counts[s_id] += 1

    last_shark = interrogation_history[-1].get("shark_id") if interrogation_history else None
    next_shark = None
    for s_id in shark_order:
        if s_id != last_shark and counts[s_id] == min(counts.values()):
            next_shark = s_id
            break
    if not next_shark:
        next_shark = shark_order[(len(interrogation_history)) % len(shark_order)]

    bank = FALLBACK_QUESTIONS[next_shark]
    idx = counts[next_shark] % len(bank)
    q_template = bank[idx]
    question = q_template.format(
        startup_name=startup_name,
        target_customer=target_customer,
        building=building,
        problem=problem,
        business_model=business_model
    )

    contradiction_warning = None
    if interrogation_history:
        last_ans = interrogation_history[-1].get("answer", "").strip()
        last_ans_lower = last_ans.lower()
        word_count = len(last_ans.split())

        is_refinement = any(w in last_ans_lower for w in ["revise", "revised", "adjust", "adjusted", "pivot", "recalculate", "instead", "changed", "lower to", "reduce to", "adapt"])
        is_honesty = any(w in last_ans_lower for w in ["cannot prevent", "limitation", "tradeoff", "challenge", "admit", "risk", "hard to", "leakage", "realistic"])

        if is_refinement or is_honesty:
            contradiction_warning = None
        elif word_count < 5:
            contradiction_warning = "Founder answer was extremely brief and lacked substantive detail."
        elif any(vague_word in last_ans_lower for vague_word in ["don't know", "tbd", "working on it", "maybe"]):
            contradiction_warning = "Founder expressed unresolved uncertainty on key business strategy parameters."

    return {
        "shark_id": next_shark,
        "shark_name": INVESTOR_PERSONAS[next_shark]["name"],
        "contradiction_warning": contradiction_warning,
        "question": question,
        "is_fallback": True,
        "fallback_reason": "AI temporarily unavailable — using Investor Backup Question"
    }


def get_fallback_evaluation(
    pitch_data: Dict[str, str],
    interrogation_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculates a deterministic investment scorecard when Gemini is unavailable."""
    startup_name = pitch_data.get("startup_name") or "The Startup"

    num_answers = len(interrogation_history)
    total_words = sum(len(turn.get("answer", "").split()) for turn in interrogation_history)
    avg_words = (total_words / num_answers) if num_answers > 0 else 0

    combined_text = (
        " ".join([pitch_data.get(k, "") for k in pitch_data]) + " " +
        " ".join([turn.get("answer", "") for turn in interrogation_history])
    ).lower()

    refinement_count = sum(1 for turn in interrogation_history if any(w in turn.get("answer", "").lower() for w in ["revise", "revised", "adjust", "adjusted", "pivot", "recalculate", "instead", "changed", "lower", "reduce", "adapt"]))
    honesty_count = sum(1 for turn in interrogation_history if any(w in turn.get("answer", "").lower() for w in ["cannot prevent", "limitation", "tradeoff", "challenge", "admit", "risk", "hard to", "leakage", "realistic"]))

    coachability_bonus = min(10, (refinement_count * 3) + (honesty_count * 3))

    has_metrics = any(w in combined_text for w in ["%", "$", "cac", "ltv", "margin", "arr", "mrr", "revenue", "cost"])
    has_moat = any(w in combined_text for w in ["patent", "ip", "proprietary", "network effect", "lock-in", "moat", "flywheel"])
    has_market = any(w in combined_text for w in ["tam", "market", "customer", "b2b", "enterprise", "smb", "consumer"])
    has_tech = any(w in combined_text for w in ["api", "ai", "architecture", "cloud", "stack", "algorithm", "scale"])

    problem_score = 75 + (5 if len(pitch_data.get("problem", "")) > 40 else 0)
    market_score = 70 + (10 if has_market else 0) + (5 if avg_words > 25 else 0) + (coachability_bonus // 2)
    tech_score = 70 + (10 if has_tech else 0) + (5 if has_moat else 0)
    biz_score = 68 + (12 if has_metrics else 0) + (coachability_bonus // 2)
    comp_score = 65 + (10 if avg_words > 30 else 0)
    defensibility_score = 65 + (15 if has_moat else 0)

    subscores = {
        "problem": min(95, max(50, problem_score)),
        "market": min(95, max(50, market_score)),
        "technology": min(95, max(50, tech_score)),
        "business_model": min(95, max(50, biz_score)),
        "competition": min(95, max(50, comp_score)),
        "defensibility": min(95, max(50, defensibility_score))
    }

    overall_score = int(sum(subscores.values()) / len(subscores))

    if overall_score >= 85:
        final_decision = "INVEST"
    elif overall_score >= 70:
        final_decision = "INVEST WITH CONDITIONS"
    else:
        final_decision = "PASS"

    shark_verdicts = {
        "Market Shark": f"{'INVEST WITH CONDITIONS' if market_score >= 70 else 'PASS'} — Market positioning for {startup_name} shows promise; strategic refinements demonstrate team coachability.",
        "Tech Shark": f"{'INVEST' if tech_score >= 80 else 'INVEST WITH CONDITIONS'} — Technical architecture for {pitch_data.get('building', 'product')} is feasible; founder appropriately acknowledged technical limitations.",
        "Finance Shark": f"{'INVEST WITH CONDITIONS' if biz_score >= 70 else 'PASS'} — Unit economics model shows willingness to adapt pricing based on cost realities.",
        "Skeptic Shark": f"{'INVEST WITH CONDITIONS' if overall_score >= 75 else 'PASS'} — Founder demonstrated coachability under stress testing; competitive moat requires ongoing monitoring."
    }

    return {
        "overall_score": overall_score,
        "subscores": subscores,
        "shark_verdicts": shark_verdicts,
        "biggest_strength": f"Clear problem definition and team willingness to refine key assumptions for {pitch_data.get('target_customer', 'target customer')}.",
        "biggest_weakness": "Long-term customer retention and competitive moat defense.",
        "biggest_concern": "Risk of incumbent feature duplication or aggressive price competition.",
        "top_improvements": [
            f"Validate customer willingness to pay for {startup_name} via pre-orders or LOIs.",
            "Establish quantifiable unit economic benchmarks (CAC payback under 9 months).",
            "Build proprietary data network effects to protect technical moat."
        ],
        "final_decision": final_decision,
        "is_fallback": True,
        "fallback_reason": "AI temporarily unavailable — Scorecard generated via Investor Backup Evaluation Engine"
    }


# ---------------------------------------------------------
# PUBLIC AI ENGINE INTERFACES
# ---------------------------------------------------------

def generate_first_question(pitch_data: Dict[str, str]) -> Dict[str, Any]:
    """Generates the opening question from the investor panel based on pitch memo."""
    client = get_genai_client()
    if client:
        prompt = f"""
STARTUP PITCH MEMO:
- Startup Name: {pitch_data.get('startup_name')}
- Elevator Pitch: {pitch_data.get('building')}
- Problem Solved: {pitch_data.get('problem')}
- Target Customer: {pitch_data.get('target_customer')}
- Business Model: {pitch_data.get('business_model')}

This is the start of the interrogation. Select the single best Shark to open the interrogation with a sharp, challenging question about their core pitch claims.
"""
        try:
            raw_response = _call_gemini(client, prompt, SYSTEM_INTERROGATION_PROMPT)
            parsed = _clean_json_response(raw_response)

            shark_id = parsed.get("next_shark_id", "market_shark")
            if shark_id not in INVESTOR_PERSONAS:
                shark_id = "market_shark"

            return {
                "shark_id": shark_id,
                "shark_name": INVESTOR_PERSONAS[shark_id]["name"],
                "contradiction_warning": parsed.get("contradiction_warning"),
                "question": parsed.get("question", "What is your primary unfair advantage in this market?"),
                "is_fallback": False
            }
        except Exception as e:
            print(f"Gemini API unavailable for first question ({e}). Switching to deterministic fallback.")

    return get_fallback_first_question(pitch_data)


def generate_next_adaptive_question(
    pitch_data: Dict[str, str],
    interrogation_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates the next adaptive follow-up question based on pitch memo and full Q&A transcript.
    """
    client = get_genai_client()
    if client:
        formatted_history = ""
        for idx, turn in enumerate(interrogation_history, 1):
            formatted_history += f"\nTurn {idx} [{turn.get('shark_name')}]:\n"
            formatted_history += f"  Question: {turn.get('question')}\n"
            formatted_history += f"  Founder Answer: {turn.get('answer')}\n"

        prompt = f"""
STARTUP PITCH MEMO:
- Startup Name: {pitch_data.get('startup_name')}
- Elevator Pitch: {pitch_data.get('building')}
- Problem Solved: {pitch_data.get('problem')}
- Target Customer: {pitch_data.get('target_customer')}
- Business Model: {pitch_data.get('business_model')}

INTERROGATION TRANSCRIPT SO FAR:
{formatted_history}

Analyze the latest answer from the founder. Check if they dodged the question, made unsupported claims, or CONTRADICTED any statement from earlier turns or their pitch memo.
Generate the next adaptive question from the most appropriate Shark.
"""
        try:
            raw_response = _call_gemini(client, prompt, SYSTEM_INTERROGATION_PROMPT)
            parsed = _clean_json_response(raw_response)

            shark_id = parsed.get("next_shark_id", "skeptic_shark")
            if shark_id not in INVESTOR_PERSONAS:
                shark_id = "skeptic_shark"

            return {
                "shark_id": shark_id,
                "shark_name": INVESTOR_PERSONAS[shark_id]["name"],
                "contradiction_warning": parsed.get("contradiction_warning"),
                "question": parsed.get("question", "How do your unit economics support this scale?"),
                "is_fallback": False
            }
        except Exception as e:
            print(f"Gemini API unavailable for next question ({e}). Switching to deterministic fallback.")

    return get_fallback_next_question(pitch_data, interrogation_history)


def generate_final_evaluation(
    pitch_data: Dict[str, str],
    interrogation_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates comprehensive investment committee scorecard and verdict."""
    client = get_genai_client()
    if client:
        formatted_history = ""
        for idx, turn in enumerate(interrogation_history, 1):
            formatted_history += f"\nTurn {idx} [{turn.get('shark_name')}]:\n"
            formatted_history += f"  Question: {turn.get('question')}\n"
            formatted_history += f"  Founder Answer: {turn.get('answer')}\n"

        prompt = f"""
STARTUP PITCH MEMO:
- Startup Name: {pitch_data.get('startup_name')}
- Elevator Pitch: {pitch_data.get('building')}
- Problem Solved: {pitch_data.get('problem')}
- Target Customer: {pitch_data.get('target_customer')}
- Business Model: {pitch_data.get('business_model')}

COMPLETE INTERROGATION TRANSCRIPT:
{formatted_history}

Generate the final Investment Committee Scorecard and verdicts.
"""
        try:
            raw_response = _call_gemini(client, prompt, SYSTEM_EVALUATION_PROMPT)
            parsed = _clean_json_response(raw_response)
            parsed["is_fallback"] = False
            return parsed
        except Exception as e:
            print(f"Gemini API unavailable for evaluation ({e}). Switching to deterministic fallback.")

    return get_fallback_evaluation(pitch_data, interrogation_history)
