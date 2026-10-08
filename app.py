import streamlit as st
import time
import html as py_html
from typing import Any, Dict, List, Optional
from prompts import INVESTOR_PERSONAS
from ai_engine import (
    get_api_key,
    generate_first_question,
    generate_next_adaptive_question,
    generate_final_evaluation,
    get_fallback_first_question,
    get_fallback_next_question,
    get_fallback_evaluation
)
import importlib
import evaluator

try:
    from evaluator import parse_scorecard_json, compare_scorecards, PitchScorecard
except ImportError:
    importlib.reload(evaluator)
    from evaluator import parse_scorecard_json, compare_scorecards, PitchScorecard

# ═══════════════════════════════════════════════════════════
# SECURITY & ACCESSIBILITY HELPERS
# ═══════════════════════════════════════════════════════════
def esc(text: Any) -> str:
    """Escapes user and AI generated text to prevent HTML injection/XSS."""
    if text is None:
        return ""
    return py_html.escape(str(text))

# ═══════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Investor War Room — Venture Capital Interrogation Platform",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# HTML CLEAN RENDERING HELPER (PREVENTS MARKDOWN CODEBLOCKS)
# ═══════════════════════════════════════════════════════════
def html(raw_content: str):
    """
    Renders HTML safely into Streamlit without letting Markdown interpret
    leading whitespace as code blocks or empty lines as paragraph closures.
    """
    clean_lines = [line.strip() for line in raw_content.strip().splitlines() if line.strip()]
    st.markdown("".join(clean_lines), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# DESIGN SYSTEM — PREMIUM DARK-MODE CSS (ACCESSIBLE + EFFICIENT)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Premium Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    /* ── Root Theme Variables ── */
    :root {
        --c-bg-primary: #07080f;
        --c-bg-secondary: #0c0e1a;
        --c-bg-tertiary: #111427;
        --c-surface: rgba(17, 20, 39, 0.85);
        --c-surface-glass: rgba(17, 20, 39, 0.65);
        --c-surface-elevated: rgba(25, 29, 55, 0.9);
        --c-navy: #0f172a;
        --c-blue: #3b82f6;
        --c-indigo: #6366f1;
        --c-violet: #8b5cf6;
        --c-cyan: #22d3ee;
        --c-emerald: #10b981;
        --c-amber: #f59e0b;
        --c-gold: #d4a853;
        --c-rose: #f43f5e;
        --c-lavender: #a78bfa;
        --c-pearl: #e8eaf6;
        --c-text-primary: #f8fafc;
        --c-text-secondary: #cbd5e1;
        --c-text-muted: #94a3b8;
        --border-glass: rgba(139, 92, 246, 0.15);
        --border-subtle: rgba(100, 116, 139, 0.2);
        --glow-indigo: rgba(99, 102, 241, 0.3);
        --glow-cyan: rgba(34, 211, 238, 0.25);
        --glow-violet: rgba(139, 92, 246, 0.25);
        --shadow-deep: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
        --radius-lg: 20px;
        --radius-md: 14px;
        --radius-sm: 10px;
        --radius-xs: 8px;
        --transition-smooth: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        --transition-fast: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* ── Accessibility: Reduced Motion Support ── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
            scroll-behavior: auto !important;
        }
        .stApp::before {
            animation: none !important;
        }
    }

    /* ── Accessibility: Screen Reader Only Utility ── */
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }

    /* ── Accessibility: Visible Keyboard Focus Outlines ── */
    *:focus-visible,
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    [tabindex]:focus-visible {
        outline: 2px solid var(--c-cyan) !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.25) !important;
    }

    /* ── Dark Atmospheric Background ── */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .main .block-container {
        background-color: var(--c-bg-primary) !important;
        color: var(--c-text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        overflow-x: hidden;
    }

    /* Animated mesh-orb background */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-image:
            radial-gradient(ellipse 600px 400px at 15% 20%, rgba(99, 102, 241, 0.12) 0%, transparent 70%),
            radial-gradient(ellipse 500px 350px at 85% 15%, rgba(34, 211, 238, 0.08) 0%, transparent 70%),
            radial-gradient(ellipse 700px 500px at 50% 70%, rgba(139, 92, 246, 0.07) 0%, transparent 70%),
            radial-gradient(ellipse 400px 300px at 80% 80%, rgba(212, 168, 83, 0.04) 0%, transparent 60%),
            radial-gradient(circle 2px at 20% 30%, rgba(99, 102, 241, 0.35) 0%, transparent 100%),
            radial-gradient(circle 2px at 70% 25%, rgba(34, 211, 238, 0.3) 0%, transparent 100%),
            radial-gradient(circle 1.5px at 40% 65%, rgba(139, 92, 246, 0.25) 0%, transparent 100%),
            radial-gradient(circle 1px at 60% 80%, rgba(212, 168, 83, 0.2) 0%, transparent 100%),
            radial-gradient(circle 1.5px at 90% 55%, rgba(99, 102, 241, 0.2) 0%, transparent 100%);
        pointer-events: none;
        z-index: 0;
        animation: ambientDrift 30s ease-in-out infinite alternate;
    }

    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background:
            linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.4;
    }

    @keyframes ambientDrift {
        0% { transform: scale(1) translate(0, 0); opacity: 1; }
        33% { transform: scale(1.02) translate(10px, -5px); opacity: 0.9; }
        66% { transform: scale(0.98) translate(-5px, 8px); opacity: 1; }
        100% { transform: scale(1.01) translate(5px, -3px); opacity: 0.95; }
    }

    #MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }

    .block-container {
        padding: 1rem 2rem 3.5rem 2rem !important;
        max-width: 1340px !important;
        position: relative;
        z-index: 1;
    }

    /* ── Typography System ── */
    h1, h2, h3, h4, h5, h6 {
        color: var(--c-text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }
    p, span, div, li {
        color: var(--c-text-secondary);
        font-family: 'Inter', sans-serif;
    }

    /* ── Keyframe Animations ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeSlideDown {
        from { opacity: 0; transform: translateY(-12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes scalePop {
        from { opacity: 0; transform: scale(0.96); }
        to   { opacity: 1; transform: scale(1); }
    }
    @keyframes shimmerBar {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes pulseAura {
        0%, 100% { box-shadow: 0 0 0 0 var(--pulse-color, rgba(99, 102, 241, 0.4)); }
        50%      { box-shadow: 0 0 0 12px transparent; }
    }
    @keyframes pulseGlow {
        0%, 100% { opacity: 1; }
        50%      { opacity: 0.5; }
    }
    @keyframes rotateGlow {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes alertPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(244, 63, 94, 0.15), inset 0 0 0 1px rgba(244, 63, 94, 0.3); }
        50%      { box-shadow: 0 0 35px rgba(244, 63, 94, 0.3), inset 0 0 0 1.5px rgba(244, 63, 94, 0.5); }
    }
    @keyframes neuralPulse {
        0%, 100% { transform: scale(1); opacity: 0.6; }
        50% { transform: scale(1.3); opacity: 1; }
    }
    @keyframes dataFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(10px) scale(0.8); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(99, 102, 241, 0.3); }
        50% { border-color: rgba(99, 102, 241, 0.6); }
    }
    @keyframes stagger1 { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes stagger2 { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes stagger3 { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

    .anim-fade { animation: fadeSlideUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .anim-scale { animation: scalePop 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .anim-slide-right { animation: slideInRight 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }

    /* ── Reduced Motion ── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ── Glass Surface Utility ── */
    .glass {
        background: var(--c-surface-glass);
        backdrop-filter: blur(24px) saturate(150%);
        -webkit-backdrop-filter: blur(24px) saturate(150%);
        border: 1px solid var(--border-glass);
    }
    .glass-elevated {
        background: var(--c-surface-elevated);
        backdrop-filter: blur(20px) saturate(140%);
        -webkit-backdrop-filter: blur(20px) saturate(140%);
        border: 1px solid rgba(139, 92, 246, 0.2);
        box-shadow: var(--shadow-card);
    }

    /* ── Top Navigation Shell ── */
    .shell-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(11, 13, 26, 0.85);
        backdrop-filter: blur(24px) saturate(150%);
        -webkit-backdrop-filter: blur(24px) saturate(150%);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 0.7rem 1.3rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3), 0 0 60px rgba(99, 102, 241, 0.05);
    }
    .shell-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .shell-logo-badge {
        width: 38px; height: 38px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #22d3ee 100%);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 11px;
        font-size: 1.15rem;
        font-weight: 900;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(165, 180, 252, 0.3);
        position: relative;
    }
    .shell-logo-badge::after {
        content: "";
        position: absolute;
        inset: -2px;
        border-radius: 13px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.4), rgba(34, 211, 238, 0.2));
        z-index: -1;
        filter: blur(6px);
    }
    .shell-title-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--c-text-primary) !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .shell-sub-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6rem;
        font-weight: 600;
        letter-spacing: 0.16em;
        color: var(--c-lavender) !important;
        text-transform: uppercase;
    }
    .shell-stepper {
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .shell-step-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.7rem;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--c-text-muted);
        font-family: 'JetBrains Mono', monospace;
        transition: var(--transition-fast);
    }
    .shell-step-item.is-active {
        color: #ffffff !important;
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        box-shadow: 0 2px 12px rgba(99, 102, 241, 0.4);
    }
    .shell-step-item.is-done {
        color: var(--c-text-secondary);
        background: rgba(99, 102, 241, 0.1);
    }
    .shell-step-item .step-num { color: var(--c-cyan); font-weight: 800; }
    .shell-step-item.is-active .step-num { color: var(--c-cyan); }
    .shell-step-arrow { color: var(--c-text-muted); font-size: 0.7rem; opacity: 0.5; }

    .shell-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        background: rgba(16, 185, 129, 0.1);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
    }
    .pulse-dot-green {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
        animation: pulseGlow 2s ease-in-out infinite;
    }
    .pulse-dot-amber {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #f59e0b;
        box-shadow: 0 0 8px rgba(245, 158, 11, 0.6);
        animation: pulseGlow 2s ease-in-out infinite;
    }

    /* ── Hero Section ── */
    .hero-panel {
        background: rgba(11, 13, 26, 0.8);
        backdrop-filter: blur(30px) saturate(150%);
        -webkit-backdrop-filter: blur(30px) saturate(150%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 28px;
        padding: 3.5rem 2.5rem 2.5rem;
        text-align: center;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.5), 0 0 80px rgba(99, 102, 241, 0.08);
    }
    .hero-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #6366f1 20%, #22d3ee 40%, #8b5cf6 60%, #d4a853 80%, transparent 100%);
        background-size: 200% auto;
        animation: shimmerBar 4s linear infinite;
    }
    .hero-panel::after {
        content: "";
        position: absolute;
        top: -50%; left: -50%; right: -50%; bottom: -50%;
        background: radial-gradient(ellipse at 50% 0%, rgba(99, 102, 241, 0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    .hero-tag-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        color: var(--c-lavender) !important;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.25);
        padding: 0.35rem 1rem;
        border-radius: 30px;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    .hero-title-main {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 3.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.045em !important;
        line-height: 1.05 !important;
        margin: 0 0 1rem 0 !important;
        position: relative;
        z-index: 1;
    }
    .hero-title-gradient {
        background: linear-gradient(135deg, #e0e7ff 0%, #818cf8 25%, #22d3ee 50%, #a78bfa 75%, #d4a853 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 4px 24px rgba(99, 102, 241, 0.3));
    }
    .hero-title-white {
        color: #f1f5f9 !important;
        -webkit-text-fill-color: #f1f5f9;
    }
    .hero-tagline {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--c-text-secondary) !important;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
        position: relative;
        z-index: 1;
    }
    .hero-explanation {
        font-size: 0.95rem;
        color: var(--c-text-muted) !important;
        max-width: 660px;
        margin: 0 auto 2rem;
        line-height: 1.7;
        position: relative;
        z-index: 1;
    }

    .hero-pipeline-strip {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        background: rgba(17, 20, 39, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: var(--radius-md);
        padding: 0.65rem 1.5rem;
        max-width: 720px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }
    .pipeline-node {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.73rem;
        font-weight: 600;
        color: var(--c-text-secondary);
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        transition: var(--transition-fast);
    }
    .pipeline-node:hover {
        background: rgba(99, 102, 241, 0.1);
        color: var(--c-lavender);
    }
    .pipeline-node .num { color: var(--c-cyan); font-weight: 800; }
    .pipeline-divider { color: var(--c-text-muted); font-size: 0.7rem; opacity: 0.4; }

    /* ── Section Titles ── */
    .section-header-block {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 1.1rem;
        padding: 0 0.15rem;
    }
    .section-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--c-cyan) !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.15rem;
    }
    .section-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--c-text-primary) !important;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .section-badge-info {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--c-text-muted);
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.15);
        padding: 0.22rem 0.65rem;
        border-radius: 6px;
    }

    /* ── Investor Persona Cards ── */
    .investor-card {
        background: rgba(17, 20, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 18px;
        padding: 1.35rem 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: var(--transition-smooth);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .investor-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--inv-accent-grad, linear-gradient(90deg, #6366f1, #22d3ee));
        transition: height 0.25s ease;
    }
    .investor-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 20px 40px -8px var(--inv-shadow-glow, rgba(99, 102, 241, 0.2)), var(--shadow-glow);
        border-color: var(--inv-main-color, rgba(99, 102, 241, 0.3));
    }
    .investor-card:hover::before { height: 4px; }
    .investor-card.is-interrogating {
        border: 1.5px solid var(--inv-main-color, #6366f1) !important;
        background: rgba(25, 29, 55, 0.9);
        box-shadow: 0 0 40px var(--inv-shadow-glow, rgba(99, 102, 241, 0.25)), 0 12px 36px rgba(0, 0, 0, 0.3) !important;
        --pulse-color: var(--inv-shadow-glow, rgba(99, 102, 241, 0.4));
        animation: pulseAura 3s infinite;
    }
    .investor-top-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
    }
    .investor-avatar-box {
        width: 46px; height: 46px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        background: var(--inv-bg-dark, rgba(99, 102, 241, 0.12));
        border: 1px solid var(--inv-border-dark, rgba(99, 102, 241, 0.2));
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .investor-card:hover .investor-avatar-box {
        transform: scale(1.12) rotate(3deg);
    }
    .investor-id-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.64rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        background: rgba(99, 102, 241, 0.08);
        color: var(--c-text-muted);
        letter-spacing: 0.06em;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    .investor-name-heading {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--c-text-primary) !important;
        letter-spacing: -0.01em;
        margin-bottom: 0.15rem;
    }
    .investor-quote-personality {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--inv-main-color, #6366f1) !important;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    .investor-role-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 700;
        color: var(--c-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .investor-description-body {
        font-size: 0.82rem;
        color: var(--c-text-secondary);
        line-height: 1.55;
        flex-grow: 1;
        margin-bottom: 0.85rem;
    }
    .pill-tag {
        display: inline-block;
        font-size: 0.64rem;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.08);
        color: var(--c-text-secondary);
        border: 1px solid rgba(99, 102, 241, 0.12);
        padding: 0.18rem 0.5rem;
        border-radius: 6px;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }

    /* ── Feature Cards ── */
    .feature-card {
        background: rgba(17, 20, 39, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.35rem;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: var(--transition-smooth);
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25), var(--shadow-glow);
        border-color: rgba(99, 102, 241, 0.25);
    }
    .feature-icon-bubble {
        width: 40px; height: 40px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        margin-bottom: 0.85rem;
    }

    /* ── Form Inputs & Textarea (Dark Theme) ── */
    label, .stTextInput label, .stTextArea label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: var(--c-text-secondary) !important;
        font-weight: 700 !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        font-family: 'JetBrains Mono', monospace !important;
        margin-bottom: 0.3rem !important;
    }
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stForm"] input,
    [data-testid="stForm"] textarea {
        background: rgba(17, 20, 39, 0.8) !important;
        color: var(--c-text-primary) !important;
        border: 1.5px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        line-height: 1.55 !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.15) !important;
        transition: border-color 0.25s, box-shadow 0.25s, background 0.25s !important;
        caret-color: var(--c-cyan) !important;
    }
    .stTextInput input:hover,
    .stTextArea textarea:hover {
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--c-indigo) !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12), inset 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        background: rgba(20, 24, 45, 0.9) !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    ::placeholder {
        color: var(--c-text-muted) !important;
        opacity: 0.7 !important;
        font-weight: 400 !important;
    }

    /* ── Button Hierarchy ── */
    button[kind="primary"],
    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"],
    div.stFormSubmitButton > button[kind="primary"],
    div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #312e81 0%, #4f46e5 40%, #6366f1 70%, #22d3ee 100%) !important;
        background-size: 200% auto !important;
        color: #ffffff !important;
        border: 1px solid rgba(165, 180, 252, 0.3) !important;
        border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.02em !important;
        padding: 0.75rem 1.6rem !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35), 0 0 0 1px rgba(99, 102, 241, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
    }
    button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover,
    div.stFormSubmitButton > button:first-child:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.5), 0 0 24px rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(165, 180, 252, 0.5) !important;
        background-position: 100% 0 !important;
    }
    button[kind="primary"]:active,
    [data-testid="stBaseButton-primary"]:active,
    div.stFormSubmitButton > button:first-child:active {
        transform: scale(0.98) !important;
    }
    button[kind="primary"] p,
    button[kind="primary"] span,
    [data-testid="stBaseButton-primary"] p,
    [data-testid="stBaseButton-primary"] span,
    div.stFormSubmitButton > button:first-child p,
    div.stFormSubmitButton > button:first-child span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    button[kind="secondary"],
    .stButton > button[kind="secondary"],
    [data-testid="stBaseButton-secondary"],
    div.stFormSubmitButton > button[kind="secondary"] {
        background: rgba(17, 20, 39, 0.7) !important;
        color: var(--c-text-primary) !important;
        border: 1.5px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.7rem 1.4rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
        transition: var(--transition-fast) !important;
    }
    button[kind="secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover {
        border-color: var(--c-indigo) !important;
        background: rgba(25, 29, 55, 0.8) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.15) !important;
    }
    button[kind="secondary"] p,
    button[kind="secondary"] span,
    [data-testid="stBaseButton-secondary"] p,
    [data-testid="stBaseButton-secondary"] span {
        color: var(--c-text-primary) !important;
        font-weight: 600 !important;
    }

    /* ── War Room Arena ── */
    .wr-banner-header {
        background: rgba(11, 13, 26, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.3rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }
    .wr-stats-group {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    .wr-stat-cell { display: flex; flex-direction: column; }
    .wr-stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.63rem;
        font-weight: 700;
        color: var(--c-text-muted);
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .wr-stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--c-text-primary);
    }

    .question-stage-card {
        background: rgba(17, 20, 39, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-bottom: 1.3rem;
        box-shadow: var(--shadow-card), 0 0 50px rgba(99, 102, 241, 0.06);
        position: relative;
        overflow: hidden;
    }
    .question-stage-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 4px;
        background: var(--q-accent-grad, linear-gradient(180deg, #6366f1, #22d3ee));
    }
    .question-top-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.1);
    }
    .question-investor-info {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .question-quote-box {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--c-text-primary) !important;
        line-height: 1.7;
        letter-spacing: -0.01em;
        background: rgba(99, 102, 241, 0.05);
        border: 1px solid rgba(99, 102, 241, 0.1);
        padding: 1.5rem 1.6rem;
        border-radius: var(--radius-md);
        position: relative;
    }
    .question-quote-box::before {
        content: "\\201C";
        position: absolute;
        top: 0.5rem; left: 1rem;
        font-size: 2.5rem;
        color: var(--c-indigo);
        opacity: 0.3;
        font-family: 'Space Grotesk', serif;
        line-height: 1;
    }

    /* ── Contradiction Callout ── */
    .contradiction-callout {
        background: rgba(244, 63, 94, 0.08);
        border: 1.5px solid rgba(244, 63, 94, 0.3);
        border-radius: var(--radius-md);
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.25rem;
        animation: alertPulse 3s infinite;
        position: relative;
        overflow: hidden;
    }
    .contradiction-callout::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #f43f5e, #ef4444, #f97316, #f43f5e);
        background-size: 200% auto;
        animation: shimmerBar 3s linear infinite;
    }
    .contradiction-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        font-weight: 800;
        color: #fb7185;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .contradiction-body {
        font-size: 0.9rem;
        color: #fda4af;
        line-height: 1.55;
        font-weight: 500;
    }

    /* ── Transcript Timeline ── */
    .timeline-node-card {
        background: rgba(17, 20, 39, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        transition: var(--transition-fast);
    }
    .timeline-node-card:hover {
        border-color: rgba(99, 102, 241, 0.25);
    }
    .timeline-q-bubble {
        background: rgba(99, 102, 241, 0.06);
        border-left: 3px solid var(--c-indigo);
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: var(--c-text-secondary);
        margin-bottom: 0.5rem;
        line-height: 1.55;
    }
    .timeline-a-bubble {
        background: rgba(212, 168, 83, 0.06);
        border-left: 3px solid var(--c-gold);
        padding: 0.8rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: var(--c-text-primary);
        line-height: 1.55;
    }

    /* ── Scorecard & Metrics ── */
    .verdict-hero-card {
        background: rgba(17, 20, 39, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: var(--radius-lg);
        padding: 1.8rem 2rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
    }
    .verdict-hero-card.invest-pass {
        border: 1.5px solid rgba(239, 68, 68, 0.4);
        background: linear-gradient(135deg, rgba(17, 20, 39, 0.9) 0%, rgba(127, 29, 29, 0.15) 100%);
    }
    .verdict-hero-card.invest-cond {
        border: 1.5px solid rgba(245, 158, 11, 0.4);
        background: linear-gradient(135deg, rgba(17, 20, 39, 0.9) 0%, rgba(146, 64, 14, 0.15) 100%);
    }
    .verdict-hero-card.invest-yes {
        border: 1.5px solid rgba(16, 185, 129, 0.4);
        background: linear-gradient(135deg, rgba(17, 20, 39, 0.9) 0%, rgba(6, 95, 70, 0.15) 100%);
    }
    .verdict-stamp-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .verdict-title-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .verdict-subtext {
        font-size: 0.92rem;
        line-height: 1.6;
        color: var(--c-text-secondary);
    }

    .score-gauge-card {
        background: rgba(17, 20, 39, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: var(--shadow-card);
    }

    .dim-metric-card {
        background: rgba(17, 20, 39, 0.75);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1.1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: var(--transition-smooth);
    }
    .dim-metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3), var(--shadow-glow);
        border-color: rgba(99, 102, 241, 0.25);
    }
    .dim-metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .dim-metric-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 700;
        color: var(--c-text-muted);
        letter-spacing: 0.08em;
    }
    .dim-metric-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.5rem;
        animation: countUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .dim-metric-bar {
        height: 5px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.4rem;
    }
    .dim-metric-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 0 8px currentColor;
    }
    .dim-metric-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.06em;
    }

    .round-delta-strip {
        background: rgba(16, 185, 129, 0.06);
        border: 1.5px solid rgba(16, 185, 129, 0.2);
        border-radius: 16px;
        padding: 1.1rem 1.8rem;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.08);
    }
    .round-delta-cell { text-align: center; }
    .round-delta-lbl {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #34d399;
    }
    .round-delta-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--c-text-primary);
    }

    /* ── AI Processing Visualization ── */
    .ai-processing-card {
        background: rgba(11, 13, 26, 0.85);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: var(--radius-lg);
        padding: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .ai-processing-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--c-indigo), var(--c-cyan), var(--c-violet), transparent);
        background-size: 200% auto;
        animation: shimmerBar 2s linear infinite;
    }
    .neural-dots {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-bottom: 1rem;
    }
    .neural-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--c-indigo);
        animation: neuralPulse 1.5s ease-in-out infinite;
    }
    .neural-dot:nth-child(2) { animation-delay: 0.2s; background: var(--c-cyan); }
    .neural-dot:nth-child(3) { animation-delay: 0.4s; background: var(--c-violet); }
    .neural-dot:nth-child(4) { animation-delay: 0.6s; background: var(--c-lavender); }
    .neural-dot:nth-child(5) { animation-delay: 0.8s; background: var(--c-cyan); }

    /* ── Expander Styling ── */
    [data-testid="stExpander"] {
        background: rgba(17, 20, 39, 0.6) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--c-text-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary span {
        color: var(--c-text-primary) !important;
    }

    /* ── Status/Spinner ── */
    [data-testid="stStatusWidget"] {
        background: rgba(17, 20, 39, 0.85) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: var(--radius-md) !important;
        color: var(--c-text-primary) !important;
    }
    [data-testid="stStatusWidget"] label,
    [data-testid="stStatusWidget"] p,
    [data-testid="stStatusWidget"] span {
        color: var(--c-text-primary) !important;
    }

    /* ── Warning/Error Messages ── */
    [data-testid="stAlert"] {
        background: rgba(17, 20, 39, 0.8) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ── Responsive Design ── */
    @media (max-width: 1024px) {
        .shell-stepper { display: none !important; }
        .hero-title-main { font-size: 2.6rem !important; }
        .hero-pipeline-strip { flex-wrap: wrap; gap: 0.3rem; }
        .wr-stats-group { gap: 1rem; }
        .block-container { padding: 0.8rem 1rem 3rem 1rem !important; }
    }

    @media (max-width: 768px) {
        .shell-container { padding: 0.5rem 0.8rem; }
        .shell-status-badge { display: none !important; }
        .hero-title-main { font-size: 2rem !important; }
        .hero-panel { padding: 2rem 1.2rem 1.5rem; border-radius: 20px; }
        .hero-pipeline-strip { display: none !important; }
        .question-stage-card { padding: 1.2rem; }
        .question-quote-box { font-size: 1rem; padding: 1rem; }
        .wr-banner-header { flex-direction: column; gap: 0.8rem; text-align: center; }
        .wr-stats-group { flex-wrap: wrap; justify-content: center; }
        .round-delta-strip { flex-direction: column; gap: 1rem; }
    }

    @media (max-width: 480px) {
        .hero-title-main { font-size: 1.7rem !important; }
        .block-container { padding: 0.5rem 0.6rem 2.5rem 0.6rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE (UNTOUCHED LOGIC)
# ═══════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "pitch_data" not in st.session_state:
    st.session_state.pitch_data = {
        "startup_name": "", "building": "", "problem": "",
        "target_customer": "", "business_model": ""
    }
if "interrogation_history" not in st.session_state:
    st.session_state.interrogation_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "previous_scorecard" not in st.session_state:
    st.session_state.previous_scorecard = None
if "answer_input" not in st.session_state:
    st.session_state.answer_input = ""
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "is_submitting" not in st.session_state:
    st.session_state.is_submitting = False

# ═══════════════════════════════════════════════════════════
# INVESTOR SHARK VISUAL CONFIGURATION
# ═══════════════════════════════════════════════════════════
SHARK_META = {
    "market_shark": {
        "main_color": "#22d3ee",
        "grad": "linear-gradient(135deg, #06b6d4, #22d3ee, #10b981)",
        "bg_dark": "rgba(6, 182, 212, 0.1)",
        "border_dark": "rgba(6, 182, 212, 0.2)",
        "shadow_glow": "rgba(6, 182, 212, 0.25)",
        "quote": '"Does anyone actually want this?"',
        "role": "Market Intelligence & Demand",
        "specs": "TAM · ICP · Distribution Velocity",
        "desc": "Challenges go-to-market speed, ICP definition, distribution channels, and addressable market realism.",
        "pills": ["Target Customer Profile", "TAM / SAM / SOM"],
        "processing_msg": "Analyzing customer demand patterns..."
    },
    "tech_shark": {
        "main_color": "#818cf8",
        "grad": "linear-gradient(135deg, #6366f1, #818cf8, #a78bfa)",
        "bg_dark": "rgba(99, 102, 241, 0.1)",
        "border_dark": "rgba(99, 102, 241, 0.2)",
        "shadow_glow": "rgba(99, 102, 241, 0.25)",
        "quote": '"Can you actually build and scale it?"',
        "role": "Deep Tech Architecture & Scalability",
        "specs": "Architecture · Moat · Proprietary IP",
        "desc": "Audits infrastructure feasibility, tech debt, defensible IP barriers, and distributed scale limits.",
        "pills": ["Core Tech Stack", "Defensible Moat"],
        "processing_msg": "Stress-testing technical feasibility..."
    },
    "finance_shark": {
        "main_color": "#fbbf24",
        "grad": "linear-gradient(135deg, #f59e0b, #fbbf24, #d4a853)",
        "bg_dark": "rgba(245, 158, 11, 0.1)",
        "border_dark": "rgba(245, 158, 11, 0.2)",
        "shadow_glow": "rgba(245, 158, 11, 0.25)",
        "quote": '"Will this generate venture returns?"',
        "role": "Financial Discipline & Unit Economics",
        "specs": "Payback · Margins · Burn Multiple",
        "desc": "Dissects monetization mechanics, gross margins, CAC payback cycles, and path to venture profitability.",
        "pills": ["Unit Economics", "CAC / LTV Payback"],
        "processing_msg": "Evaluating unit economics..."
    },
    "skeptic_shark": {
        "main_color": "#fb7185",
        "grad": "linear-gradient(135deg, #f43f5e, #fb7185, #a78bfa)",
        "bg_dark": "rgba(244, 63, 94, 0.1)",
        "border_dark": "rgba(244, 63, 94, 0.2)",
        "shadow_glow": "rgba(244, 63, 94, 0.25)",
        "quote": '"What are you not telling us?"',
        "role": "Risk Auditor & Contradiction Police",
        "specs": "Assumptions · Contradictions · Logic Flaws",
        "desc": "Forensically probes unverified claims, logical fallacies, and discrepancies between past statements.",
        "pills": ["Contradiction Matrix", "Execution Blindspots"],
        "processing_msg": "Searching for contradictions..."
    }
}

# ═══════════════════════════════════════════════════════════
# REUSABLE PRESENTATION COMPONENTS
# ═══════════════════════════════════════════════════════════
def render_shell():
    pg = st.session_state.page
    has_key = bool(get_api_key())
    status_label = "GEMINI ENGINE ONLINE" if has_key else "BACKUP MODE ACTIVE"
    dot_class = "pulse-dot-green" if has_key else "pulse-dot-amber"

    s1 = "is-active" if pg in ("landing", "pitch_form") else "is-done"
    s2 = "is-active" if pg == "war_room" else ("is-done" if pg == "evaluation" else "")
    s3 = "is-active" if pg == "evaluation" else ""

    html(f"""
    <div class="shell-container anim-fade">
        <div class="shell-brand">
            <div class="shell-logo-badge">✦</div>
            <div>
                <div class="shell-title-text">AI INVESTOR WAR ROOM</div>
                <div class="shell-sub-text">VENTURE CAPITAL INTELLIGENCE</div>
            </div>
        </div>
        <div class="shell-stepper">
            <div class="shell-step-item {s1}"><span class="step-num">01</span> MEMO</div>
            <span class="shell-step-arrow">→</span>
            <div class="shell-step-item {s2}"><span class="step-num">02</span> WAR ROOM</div>
            <span class="shell-step-arrow">→</span>
            <div class="shell-step-item {s3}"><span class="step-num">03</span> VERDICT</div>
        </div>
        <div class="shell-status-badge">
            <span class="{dot_class}"></span>
            <span>{status_label}</span>
        </div>
    </div>
    """)

def render_api_warning():
    html("""
    <div style="background:rgba(245, 158, 11, 0.08); border:1px solid rgba(245, 158, 11, 0.25); border-left:3px solid #f59e0b; border-radius:12px; padding:0.9rem 1.25rem; margin-bottom:1.3rem;">
        <div style="font-family:'JetBrains Mono',monospace; font-weight:700; color:#fbbf24; font-size:0.73rem; letter-spacing:0.08em; margin-bottom:0.2rem;">
            ⚠ GEMINI API KEY — BACKUP MODE
        </div>
        <div style="color:#fcd34d; font-size:0.85rem; line-height:1.5; opacity:0.85;">
            Operating on deterministic backup question logic. Configure <code style="background:rgba(251,191,36,0.12); padding:0.15rem 0.4rem; border-radius:4px; color:#fbbf24;">GEMINI_API_KEY</code> in <code style="background:rgba(251,191,36,0.12); padding:0.15rem 0.4rem; border-radius:4px; color:#fbbf24;">.env</code> for live Gemini intelligence.
        </div>
    </div>
    """)

def render_svg_score_ring(score: int) -> str:
    circumference = 301.59
    offset = circumference * (1.0 - max(0, min(100, score)) / 100.0)

    if score >= 80:
        c1, c2 = "#10b981", "#22d3ee"
        badge_txt = "HIGH CONVICTION"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        badge_clr = "#34d399"
    elif score >= 70:
        c1, c2 = "#f59e0b", "#d4a853"
        badge_txt = "CONDITIONAL"
        badge_bg = "rgba(245, 158, 11, 0.15)"
        badge_clr = "#fbbf24"
    else:
        c1, c2 = "#ef4444", "#f43f5e"
        badge_txt = "NEEDS WORK"
        badge_bg = "rgba(239, 68, 68, 0.15)"
        badge_clr = "#fb7185"

    return f"""
    <div class="score-gauge-card anim-scale">
        <svg width="160" height="160" viewBox="0 0 120 120" role="img" aria-label="Score: {score} out of 100">
            <defs>
                <linearGradient id="scoreRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{c1}" />
                    <stop offset="100%" stop-color="{c2}" />
                </linearGradient>
                <filter id="ringGlow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>
            <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(99, 102, 241, 0.08)" stroke-width="8" />
            <circle cx="60" cy="60" r="48" fill="none" stroke="url(#scoreRingGrad)" stroke-width="8"
                    stroke-dasharray="301.59" stroke-dashoffset="{offset:.2f}"
                    stroke-linecap="round" transform="rotate(-90 60 60)" filter="url(#ringGlow)" />
            <text x="60" y="56" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="30" font-weight="700" fill="{c1}">{score}</text>
            <text x="60" y="74" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="600" fill="#64748b">/ 100</text>
        </svg>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.66rem; font-weight:700; letter-spacing:0.1em; color:#64748b; margin-top:0.3rem;">
            SYNDICATE COMPOSITE
        </div>
        <div style="background:{badge_bg}; color:{badge_clr}; font-family:'JetBrains Mono',monospace; font-size:0.64rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:12px; margin-top:0.3rem;">
            {badge_txt}
        </div>
    </div>
    """

# ═══════════════════════════════════════════════════════════
# EXECUTE SHELL
# ═══════════════════════════════════════════════════════════
render_shell()

# ═══════════════════════════════════════════════════════════
# PAGE 1: LANDING PAGE
# ═══════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    html("""
    <div class="hero-panel anim-scale">
        <div class="hero-tag-badge">
            <span>✦</span>
            <span>AI-POWERED INVESTMENT COMMITTEE</span>
            <span>✦</span>
        </div>
        <h1 class="hero-title-main">
            <span class="hero-title-white">AI INVESTOR</span><br>
            <span class="hero-title-gradient">WAR ROOM</span>
        </h1>
        <div class="hero-tagline">
            Stress-test your startup assumptions before venture capitalists do.
        </div>
        <div class="hero-explanation">
            Four specialized AI investors cross-examine your venture across demand, architecture,
            unit economics, and execution risks — then deliver an institutional-grade investment verdict.
        </div>
        <div class="hero-pipeline-strip">
            <div class="pipeline-node"><span class="num">01</span> MEMO INTAKE</div>
            <span class="pipeline-divider">→</span>
            <div class="pipeline-node"><span class="num">02</span> INTERROGATION</div>
            <span class="pipeline-divider">→</span>
            <div class="pipeline-node"><span class="num">03</span> STRESS-TEST</div>
            <span class="pipeline-divider">→</span>
            <div class="pipeline-node"><span class="num">04</span> TERM SHEET</div>
        </div>
    </div>
    """)

    if not get_api_key():
        render_api_warning()

    html("""
    <div class="section-header-block">
        <div>
            <div class="section-eyebrow">THE SYNDICATE</div>
            <div class="section-title">The 4 Investor Partners</div>
        </div>
        <div class="section-badge-info">AUTONOMOUS VC PANEL</div>
    </div>
    """)

    c_sharks = st.columns(4)
    shark_items = list(INVESTOR_PERSONAS.values())
    for idx, col in enumerate(c_sharks):
        s = shark_items[idx]
        sid = s["id"]
        meta = SHARK_META[sid]
        with col:
            pills_html = "".join([f'<span class="pill-tag">{p}</span>' for p in meta['pills']])
            html(f"""
            <div class="investor-card anim-fade delay-{idx+1}" style="
                --inv-accent-grad: {meta['grad']};
                --inv-main-color: {meta['main_color']};
                --inv-bg-dark: {meta['bg_dark']};
                --inv-border-dark: {meta['border_dark']};
                --inv-shadow-glow: {meta['shadow_glow']};
                --inv-border-glow: {meta['main_color']};
            ">
                <div class="investor-top-row">
                    <div class="investor-avatar-box">{s['avatar']}</div>
                    <span class="investor-id-tag">{sid.split('_')[0].upper()}</span>
                </div>
                <div class="investor-name-heading">{s['name']}</div>
                <div class="investor-quote-personality">{meta['quote']}</div>
                <div class="investor-role-title">{meta['role']}</div>
                <div style="font-size:0.73rem; font-weight:600; color:{meta['main_color']}; margin-bottom:0.5rem; font-family:'JetBrains Mono',monospace;">
                    {meta['specs']}
                </div>
                <div class="investor-description-body">{meta['desc']}</div>
                <div>{pills_html}</div>
            </div>
            """)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    feature_data = [
        ("⚡", "rgba(99, 102, 241, 0.12)", "#818cf8", "Dynamic Adaptive Questions", "Each follow-up question is synthesized in real-time from your exact defense, probing weaknesses and avoiding generic scripted queries."),
        ("🔍", "rgba(244, 63, 94, 0.12)", "#fb7185", "Contradiction Matrix Engine", "Identifies discrepancies when your live answers diverge from earlier claims or pitch memo metrics, forcing intellectual consistency."),
        ("🏆", "rgba(16, 185, 129, 0.12)", "#34d399", "Institutional Due Diligence", "6-axis weighted scoring, partner syndicate vote consensus, top risks breakdown, and prioritized operational roadmap.")
    ]
    for col, (icon, bg, clr, title, body) in zip([f1, f2, f3], feature_data):
        with col:
            html(f"""
            <div class="feature-card">
                <div class="feature-icon-bubble" style="background:{bg}; color:{clr};">{icon}</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.02rem; color:var(--c-text-primary); margin-bottom:0.35rem;">{title}</div>
                <div style="font-size:0.84rem; color:var(--c-text-muted); line-height:1.6;">{body}</div>
            </div>
            """)

    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

    c_left, c_btn, c_right = st.columns([1, 1.8, 1])
    with c_btn:
        if st.button("ENTER THE WAR ROOM →", use_container_width=True, type="primary"):
            st.session_state.page = "pitch_form"
            st.rerun()

# ═══════════════════════════════════════════════════════════
# PAGE 2: PITCH MEMO INTAKE FORM
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "pitch_form":
    html("""
    <div style="background:rgba(11, 13, 26, 0.85); backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px); border:1px solid rgba(99, 102, 241, 0.12); border-radius:20px; padding:2rem 2.2rem 1.6rem; margin-bottom:1.3rem; box-shadow:0 8px 40px rgba(0, 0, 0, 0.3); position:relative; overflow:hidden;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg, #6366f1, #22d3ee, #8b5cf6); background-size:200% auto; animation:shimmerBar 4s linear infinite;"></div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="section-eyebrow">STAGE 01 : VENTURE INTAKE</div>
                <h2 style="font-size:1.75rem; margin:0.15rem 0 0.4rem; color:var(--c-text-primary) !important;">Confidential Pitch Memo</h2>
                <div style="color:var(--c-text-muted); font-size:0.9rem; max-width:680px; line-height:1.6;">
                    Provide your venture thesis below. The 4 investor partners will analyze every parameter to construct customized opening challenges.
                </div>
            </div>
            <div style="text-align:right; font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--c-text-muted); background:rgba(99, 102, 241, 0.06); border:1px solid rgba(99, 102, 241, 0.12); padding:0.5rem 0.85rem; border-radius:10px;">
                SECURITY: ENCRYPTED<br>STATUS: INTAKE BRIEF
            </div>
        </div>
    </div>
    """)

    if not get_api_key():
        render_api_warning()

    c_name, c_icp = st.columns(2)
    with c_name:
        startup_name = st.text_input(
            "STARTUP / VENTURE NAME",
            value=st.session_state.pitch_data["startup_name"],
            placeholder="e.g., NovuAI, CampusCart, OmniPay, CloudShield"
        )
    with c_icp:
        target_customer = st.text_input(
            "IDEAL CUSTOMER PROFILE (ICP)",
            value=st.session_state.pitch_data["target_customer"],
            placeholder="e.g., Mid-market CFOs, College students, DevOps teams"
        )

    building = st.text_area(
        "CORE PRODUCT & ELEVATOR PITCH",
        value=st.session_state.pitch_data["building"],
        placeholder="What is your product, core mechanism, and customer transformation? (2-3 sentences)…",
        height=95
    )

    c_prob, c_biz = st.columns(2)
    with c_prob:
        problem = st.text_area(
            "PRIMARY PROBLEM BEING SOLVED",
            value=st.session_state.pitch_data["problem"],
            placeholder="What critical friction or inefficiency exists? Why are legacy solutions inadequate?…",
            height=95
        )
    with c_biz:
        business_model = st.text_area(
            "BUSINESS & REVENUE MODEL",
            value=st.session_state.pitch_data["business_model"],
            placeholder="Pricing, monetization, take-rate, subscription tier, or margin structure…",
            height=95
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    cb_col, cs_col = st.columns([1, 2.2])
    with cb_col:
        if st.button("← Back to Overview", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with cs_col:
        if st.button("CONVENE THE INVESTMENT COMMITTEE →", use_container_width=True, type="primary"):
            if not startup_name.strip() or not building.strip():
                st.error("Please fill in Startup Name and Core Product Pitch to proceed.")
            else:
                st.session_state.pitch_data = {
                    "startup_name": startup_name.strip(),
                    "building": building.strip(),
                    "problem": problem.strip(),
                    "target_customer": target_customer.strip(),
                    "business_model": business_model.strip()
                }
                st.session_state.interrogation_history = []
                st.session_state.current_question = None
                st.session_state.turn_count = 0
                st.session_state.is_submitting = False
                st.session_state.page = "war_room"
                st.rerun()

# ═══════════════════════════════════════════════════════════
# PAGE 3: WAR ROOM (LIVE INTERROGATION)
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "war_room":
    p = st.session_state.pitch_data
    round_num = 1 if not st.session_state.previous_scorecard else 2

    html(f"""
    <div class="wr-banner-header anim-fade">
        <div class="wr-stats-group">
            <div class="wr-stat-cell">
                <span class="wr-stat-label">PORTFOLIO CANDIDATE</span>
                <span class="wr-stat-value">{esc(p['startup_name'])}</span>
            </div>
            <div class="wr-stat-cell">
                <span class="wr-stat-label">SESSION PHASE</span>
                <span class="wr-stat-value" style="color:var(--c-lavender);">ROUND 0{round_num} INTERROGATION</span>
            </div>
            <div class="wr-stat-cell">
                <span class="wr-stat-label">CHALLENGES DEFENDED</span>
                <span class="wr-stat-value">{len(st.session_state.interrogation_history)} TURNS</span>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; background:rgba(16, 185, 129, 0.08); border:1px solid rgba(16, 185, 129, 0.2); padding:0.35rem 0.85rem; border-radius:30px; font-family:'JetBrains Mono',monospace; font-size:0.7rem; font-weight:700; color:#34d399;">
            <span class="pulse-dot-green"></span>
            <span>COMMITTEE IN SESSION</span>
        </div>
    </div>
    """)

    if not get_api_key():
        render_api_warning()

    if st.session_state.current_question is None and len(st.session_state.interrogation_history) == 0:
        # AI Processing visualization
        html("""
        <div class="ai-processing-card anim-scale" style="margin-bottom:1.5rem;">
            <div class="neural-dots">
                <div class="neural-dot"></div>
                <div class="neural-dot"></div>
                <div class="neural-dot"></div>
                <div class="neural-dot"></div>
                <div class="neural-dot"></div>
            </div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:700; color:var(--c-text-primary); margin-bottom:0.3rem;">
                AI Investor Panel Convening
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--c-lavender); letter-spacing:0.06em;">
                Auditing pitch memo across 4 investment dimensions...
            </div>
        </div>
        """)
        with st.status("✦ AI Investor Panel Convening — Auditing Pitch Memo…", expanded=True) as status_box:
            st.write("Cross-examining venture assumptions against market benchmarks…")
            try:
                first_q = generate_first_question(p)
                st.session_state.current_question = first_q
                status_box.update(label="✦ Opening Investor Challenge Ready", state="complete")
            except Exception:
                st.session_state.current_question = get_fallback_first_question(p)
                status_box.update(label="✦ Backup Opening Challenge Assembled", state="complete")

    active_shark_id = st.session_state.current_question.get("shark_id", "market_shark") if st.session_state.current_question else "market_shark"

    col_arena, col_syndicate = st.columns([2.4, 1.1])

    with col_syndicate:
        html("""<div class="section-eyebrow" style="margin-bottom:0.6rem;">THE COMMITTEE</div>""")

        for s in INVESTOR_PERSONAS.values():
            sid = s["id"]
            is_active = (sid == active_shark_id)
            meta = SHARK_META[sid]

            active_cls = "is-interrogating" if is_active else ""

            if is_active:
                status_chip = f"""<span style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; font-weight:700; background:{meta['bg_dark']}; color:{meta['main_color']}; border:1px solid {meta['border_dark']}; padding:0.18rem 0.45rem; border-radius:10px;">● ACTIVE</span>"""
            else:
                status_chip = """<span style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; font-weight:600; color:var(--c-text-muted); background:rgba(99, 102, 241, 0.05); padding:0.18rem 0.45rem; border-radius:10px; border:1px solid rgba(99,102,241,0.08);">STANDBY</span>"""

            html(f"""
            <div class="investor-card {active_cls}" style="margin-bottom:0.7rem; padding:0.9rem 1rem; --inv-accent-grad:{meta['grad']}; --inv-main-color:{meta['main_color']}; --inv-bg-dark:{meta['bg_dark']}; --inv-border-dark:{meta['border_dark']}; --inv-shadow-glow:{meta['shadow_glow']}; --inv-border-glow:{meta['main_color']};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.1rem;">{s['avatar']}</span>
                        <strong style="font-family:'Space Grotesk',sans-serif; font-size:0.92rem; color:var(--c-text-primary);">{s['name']}</strong>
                    </div>
                    {status_chip}
                </div>
                <div style="font-size:0.7rem; color:{meta['main_color']}; font-weight:600; font-style:italic;">
                    {meta['quote']}
                </div>
            </div>
            """)

        with st.expander("📋 Venture Memo Details", expanded=False):
            html(f"""
            <div style="font-size:0.82rem; color:var(--c-text-secondary); line-height:1.6;" role="region" aria-label="Pitch Memo Summary">
                <p><strong style="color:var(--c-text-primary);">Venture:</strong> {esc(p['startup_name'])}</p>
                <p><strong style="color:var(--c-text-primary);">Product:</strong> {esc(p['building'])}</p>
                <p><strong style="color:var(--c-text-primary);">ICP:</strong> {esc(p['target_customer'])}</p>
                <p><strong style="color:var(--c-text-primary);">Problem:</strong> {esc(p['problem'])}</p>
                <p><strong style="color:var(--c-text-primary);">Model:</strong> {esc(p['business_model'])}</p>
            </div>
            """)

    with col_arena:
        if st.session_state.current_question:
            cq = st.session_state.current_question
            sid = cq["shark_id"]
            persona = INVESTOR_PERSONAS.get(sid, INVESTOR_PERSONAS["market_shark"])
            meta = SHARK_META.get(sid, SHARK_META["market_shark"])
            q_num = len(st.session_state.interrogation_history) + 1

            fallback_html = """<div style="background:rgba(245, 158, 11, 0.08); border:1px solid rgba(245, 158, 11, 0.2); color:#fbbf24; padding:0.35rem 0.85rem; border-radius:8px; font-size:0.74rem; font-weight:700; font-family:'JetBrains Mono',monospace; margin-bottom:1rem;" role="status">⚡ Deterministic Fallback Logic Active</div>""" if cq.get("is_fallback") else ""

            contra_html = f"""<div class="contradiction-callout anim-fade" role="alert" aria-live="assertive"><div class="contradiction-header"><span>⚠️</span><span>CONTRADICTION DETECTED BY AI AUDITOR</span></div><div class="contradiction-body">{esc(cq.get('contradiction_warning'))}</div></div>""" if cq.get("contradiction_warning") else ""

            q_display = f"0{q_num}" if q_num < 10 else str(q_num)

            html(f"""
            <div class="question-stage-card anim-scale" style="--q-accent-grad: {meta['grad']};" role="region" aria-label="Current Interrogation Challenge">
                {fallback_html}
                {contra_html}
                <div class="question-top-meta">
                    <div class="question-investor-info">
                        <div class="investor-avatar-box" style="background:{meta['bg_dark']}; border-color:{meta['border_dark']};" aria-hidden="true">
                            {persona['avatar']}
                        </div>
                        <div>
                            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:700; color:{meta['main_color']};">
                                {esc(cq['shark_name'])}
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:var(--c-text-muted); font-weight:600;">
                                {esc(meta['role'])}
                            </div>
                        </div>
                    </div>
                    <div style="background:rgba(99, 102, 241, 0.1); color:var(--c-text-primary); font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.74rem; padding:0.28rem 0.7rem; border-radius:12px; border:1px solid rgba(99,102,241,0.15);">
                        QUESTION {q_display}
                    </div>
                </div>
                <div class="question-quote-box">
                    {esc(cq['question'])}
                </div>
            </div>
            """)

            with st.form(key=f"defense_form_{st.session_state.turn_count}"):
                founder_defense = st.text_area(
                    "FOUNDER DEFENSE & EVIDENCE",
                    value="",
                    placeholder="Defend your position with specific metrics, architecture realities, unit economics, or market evidence…",
                    height=130,
                    key=f"input_area_{st.session_state.turn_count}",
                    disabled=st.session_state.is_submitting
                )

                b_sub, b_fin = st.columns([2.2, 1])
                with b_sub:
                    submit_defense = st.form_submit_button(
                        "SUBMIT DEFENSE →",
                        use_container_width=True,
                        type="primary",
                        disabled=st.session_state.is_submitting
                    )
                with b_fin:
                    finish_early = st.form_submit_button(
                        "FINISH & GET VERDICT",
                        use_container_width=True,
                        disabled=st.session_state.is_submitting
                    )

                if submit_defense:
                    if st.session_state.is_submitting:
                        st.warning("Already evaluating defense…")
                    elif not founder_defense.strip():
                        st.warning("Please articulate your defense before submitting.")
                    else:
                        st.session_state.is_submitting = True
                        try:
                            st.session_state.interrogation_history.append({
                                "shark_id": cq["shark_id"],
                                "shark_name": cq["shark_name"],
                                "question": cq["question"],
                                "answer": founder_defense.strip()
                            })

                            with st.status("✦ AI Investor Committee Deliberating…", expanded=True) as status_box:
                                st.write("Cross-checking defense against historical statements and unit metrics…")
                                time.sleep(0.3)
                                status_box.update(label="✦ Synthesizing Next Adaptive Investor Challenge…", state="running")
                                try:
                                    next_challenge = generate_next_adaptive_question(p, st.session_state.interrogation_history)
                                except Exception:
                                    next_challenge = get_fallback_next_question(p, st.session_state.interrogation_history)

                                st.session_state.current_question = next_challenge
                                status_box.update(label="✦ Next Investor Challenge Ready", state="complete")

                            st.session_state.turn_count += 1
                        finally:
                            st.session_state.is_submitting = False
                        st.rerun()

                if finish_early:
                    if st.session_state.is_submitting:
                        st.warning("Deliberation in progress…")
                    else:
                        st.session_state.is_submitting = True
                        try:
                            if len(st.session_state.interrogation_history) == 0 and founder_defense.strip():
                                st.session_state.interrogation_history.append({
                                    "shark_id": cq["shark_id"],
                                    "shark_name": cq["shark_name"],
                                    "question": cq["question"],
                                    "answer": founder_defense.strip()
                                })

                            with st.status("✦ Convening Full Syndicate for Final Investment Verdict…", expanded=True) as status_box:
                                st.write("Scoring across 6 diligence dimensions & tallying partner votes…")
                                try:
                                    eval_raw = generate_final_evaluation(p, st.session_state.interrogation_history)
                                except Exception:
                                    eval_raw = get_fallback_evaluation(p, st.session_state.interrogation_history)

                                st.session_state.evaluation_result = parse_scorecard_json(eval_raw)
                                status_box.update(label="✦ Syndicate Consensus Reached", state="complete")

                            st.session_state.page = "evaluation"
                        finally:
                            st.session_state.is_submitting = False
                        st.rerun()

    if len(st.session_state.interrogation_history) > 0:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.expander(f"📜 INTERROGATION TRANSCRIPT ({len(st.session_state.interrogation_history)} Turns)", expanded=True):
            for idx, turn in enumerate(reversed(st.session_state.interrogation_history), 1):
                p_item = INVESTOR_PERSONAS.get(turn["shark_id"], INVESTOR_PERSONAS["market_shark"])
                meta_item = SHARK_META.get(turn["shark_id"], SHARK_META["market_shark"])
                turn_seq = len(st.session_state.interrogation_history) - idx + 1
                t_display = f"0{turn_seq}" if turn_seq < 10 else str(turn_seq)

                html(f"""
                <div class="timeline-node-card" role="article" aria-label="Turn Q{t_display} with {esc(turn['shark_name'])}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:700; background:rgba(99, 102, 241, 0.1); padding:0.18rem 0.45rem; border-radius:6px; color:var(--c-lavender); border:1px solid rgba(99,102,241,0.15);">Q{t_display}</span>
                            <span style="font-size:1rem;" aria-hidden="true">{p_item['avatar']}</span>
                            <strong style="color:var(--c-text-primary); font-family:'Space Grotesk',sans-serif; font-size:0.9rem;">{esc(turn['shark_name'])}</strong>
                        </div>
                        <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:{meta_item['main_color']}; font-weight:600;">
                            {esc(meta_item['role'])}
                        </span>
                    </div>
                    <div class="timeline-q-bubble">
                        <strong style="color:var(--c-lavender);">CHALLENGE:</strong> {esc(turn['question'])}
                    </div>
                    <div class="timeline-a-bubble">
                        <strong style="color:var(--c-gold);">DEFENSE:</strong> {esc(turn['answer'])}
                    </div>
                </div>
                """)

# ═══════════════════════════════════════════════════════════
# PAGE 4: FINAL INVESTMENT VERDICT & DUE DILIGENCE SCORECARD
# ═══════════════════════════════════════════════════════════
elif st.session_state.page == "evaluation":
    res = st.session_state.evaluation_result
    p = st.session_state.pitch_data

    html(f"""
    <div class="hero-panel anim-scale" style="padding:2.2rem 2.2rem 1.8rem; margin-bottom:1.3rem;">
        <div class="hero-tag-badge">
            <span>✦</span>
            <span>INVESTMENT COMMITTEE DUE DILIGENCE REPORT</span>
            <span>✦</span>
        </div>
        <h1 class="hero-title-main" style="font-size:2.6rem !important; margin-bottom:0.4rem !important;">
            <span class="hero-title-gradient">{esc(p['startup_name'])}</span>
        </h1>
        <div class="hero-tagline" style="font-size:1.05rem; margin-bottom:0;">
            Institutional 6-Axis Diligence Scorecard & Syndicate Consensus
        </div>
    </div>
    """)

    if not res:
        st.warning("No evaluation result available.")
        if st.button("Return to War Room"):
            st.session_state.page = "war_room"
            st.rerun()
        st.stop()

    if getattr(res, "is_fallback", False):
        html("""
        <div style="background:rgba(245, 158, 11, 0.08); border:1px solid rgba(245, 158, 11, 0.2); color:#fbbf24; text-align:center; padding:0.4rem 1rem; border-radius:8px; font-size:0.76rem; font-weight:700; font-family:'JetBrains Mono',monospace; margin-bottom:1.2rem;">
            ⚡ Scorecard assembled via deterministic backup due-diligence evaluator
        </div>
        """)

    if st.session_state.previous_scorecard:
        comparison = compare_scorecards(st.session_state.previous_scorecard, res)
        prev_score = st.session_state.previous_scorecard.overall_score
        curr_score = res.overall_score
        delta = comparison["overall_delta"]
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        delta_color = "#34d399" if delta >= 0 else "#fb7185"
        summary_stmt = esc(comparison["summary_statement"])
        
        improved_pill = ""
        if comparison["improved_dimensions"]:
            dim_badges = " ".join([f"""<span style="background:rgba(52,211,153,0.12); color:#34d399; border:1px solid rgba(52,211,153,0.25); border-radius:6px; padding:0.15rem 0.5rem; font-size:0.7rem; font-family:'JetBrains Mono',monospace;">+{esc(d)}</span>""" for d in comparison["improved_dimensions"]])
            improved_pill = f"""<div style="margin-top:0.75rem; font-size:0.78rem; color:var(--c-text-secondary);"><strong>Improved Axes:</strong> {dim_badges}</div>"""

        html(f"""
        <div class="round-delta-strip anim-fade" role="region" aria-label="Round Comparison Delta">
            <div class="round-delta-cell">
                <div class="round-delta-lbl">ROUND 01 SCORE</div>
                <div class="round-delta-val">{prev_score} <span style="font-size:.85rem; color:var(--c-text-muted);">/100</span></div>
            </div>
            <div style="font-size:1.4rem; color:var(--c-text-muted);" aria-hidden="true">→</div>
            <div class="round-delta-cell">
                <div class="round-delta-lbl">ROUND 02 SCORE</div>
                <div class="round-delta-val">{curr_score} <span style="font-size:.85rem; color:var(--c-text-muted);">/100</span></div>
            </div>
            <div style="font-size:1.4rem; color:var(--c-text-muted);" aria-hidden="true">→</div>
            <div class="round-delta-cell">
                <div class="round-delta-lbl">GROWTH DELTA</div>
                <div class="round-delta-val" style="color:{delta_color};">{delta_str} PTS 🚀</div>
            </div>
        </div>
        <div style="text-align:center; font-size:0.84rem; color:var(--c-text-secondary); margin:-0.5rem 0 1.25rem;">
            {summary_stmt}
            {improved_pill}
        </div>
        """)

    verdict_text = res.final_decision.upper()
    col_verdict, col_gauge = st.columns([2.2, 1.1])

    with col_verdict:
        if "INVEST WITH CONDITIONS" in verdict_text or "CONDITIONAL" in verdict_text:
            html("""
            <div class="verdict-hero-card invest-cond anim-fade" role="region" aria-label="Syndicate Verdict">
                <div class="verdict-stamp-badge" style="color:#fbbf24;">SYNDICATE VERDICT : CONDITIONAL OFFER</div>
                <div class="verdict-title-text" style="color:#fbbf24;">⚠️ CONDITIONAL TERM SHEET</div>
                <div class="verdict-subtext">
                    The investment committee extends a conditional term sheet. Syndicate funding is contingent on successfully mitigating key customer acquisition and technical scalability risks highlighted during interrogation.
                </div>
            </div>
            """)
        elif "INVEST" in verdict_text:
            html("""
            <div class="verdict-hero-card invest-yes anim-fade" role="region" aria-label="Syndicate Verdict">
                <div class="verdict-stamp-badge" style="color:#34d399;">SYNDICATE VERDICT : UNANIMOUS OFFER</div>
                <div class="verdict-title-text" style="color:#34d399;">🎉 TERM SHEET EXTENDED</div>
                <div class="verdict-subtext">
                    The committee reached consensus to issue an institutional term sheet. Founder demonstrated exceptional conviction, defensibility, and command of core unit economics across all 4 partner interrogations.
                </div>
            </div>
            """)
        else:
            html("""
            <div class="verdict-hero-card invest-pass anim-fade" role="region" aria-label="Syndicate Verdict">
                <div class="verdict-stamp-badge" style="color:#fb7185;">SYNDICATE VERDICT : COMMITTEE PASS</div>
                <div class="verdict-title-text" style="color:#fb7185;">❌ COMMITTEE PASS</div>
                <div class="verdict-subtext">
                    The syndicate declined to issue a term sheet at this time. Structural market defensibility concerns, margin headwinds, and unresolved assumptions require further customer validation before funding.
                </div>
            </div>
            """)

    with col_gauge:
        html(render_svg_score_ring(res.overall_score))

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block" role="region" aria-label="Diligence Subscores Header">
        <div>
            <div class="section-eyebrow">DUE DILIGENCE MATRIX</div>
            <div class="section-title">6-Axis Fundamental Scores</div>
        </div>
        <div class="section-badge-info">WEIGHTED AUDIT</div>
    </div>
    """)

    subscores = res.subscores
    dimension_specs = [
        ("PROBLEM", "🎯", subscores.get("problem", 75)),
        ("MARKET", "📈", subscores.get("market", 70)),
        ("TECH", "⚡", subscores.get("technology", 70)),
        ("BIZ MODEL", "💰", subscores.get("business_model", 70)),
        ("COMPETITION", "🛡️", subscores.get("competition", 65)),
        ("DEFENSIBILITY", "🏰", subscores.get("defensibility", 65))
    ]

    cols_dim = st.columns(6)
    for i, (name, icon, score_val) in enumerate(dimension_specs):
        if score_val >= 80:
            bar_clr = "#34d399"
            tag_clr = "#34d399"
            status_text = "STRONG"
        elif score_val >= 70:
            bar_clr = "#fbbf24"
            tag_clr = "#fbbf24"
            status_text = "VIABLE"
        else:
            bar_clr = "#fb7185"
            tag_clr = "#fb7185"
            status_text = "EXPOSED"

        with cols_dim[i]:
            html(f"""
            <div class="dim-metric-card" role="group" aria-label="{esc(name)} score {score_val} out of 100">
                <div>
                    <div class="dim-metric-header">
                        <span class="dim-metric-name">{esc(name)}</span>
                        <span aria-hidden="true">{icon}</span>
                    </div>
                    <div class="dim-metric-num" style="color:{bar_clr};">
                        {score_val}
                    </div>
                </div>
                <div>
                    <div class="dim-metric-bar" role="progressbar" aria-valuenow="{score_val}" aria-valuemin="0" aria-valuemax="100">
                        <div class="dim-metric-fill" style="width:{min(100, max(0, score_val))}%; background:{bar_clr};"></div>
                    </div>
                    <div class="dim-metric-badge" style="color:{tag_clr};">
                        {status_text}
                    </div>
                </div>
            </div>
            """)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block" role="region" aria-label="Partner Deliberations Header">
        <div>
            <div class="section-eyebrow">PARTNER DELIBERATIONS</div>
            <div class="section-title">Individual Partner Votes</div>
        </div>
        <div class="section-badge-info">4 INDEPENDENT ASSESSMENTS</div>
    </div>
    """)

    col_v1, col_v2 = st.columns(2)
    verdict_keys = list(res.shark_verdicts.keys())
    for idx, key in enumerate(verdict_keys):
        target_col = col_v1 if idx % 2 == 0 else col_v2
        v_content = res.shark_verdicts[key]

        sid_match = "market_shark"
        if "Tech" in key: sid_match = "tech_shark"
        elif "Finance" in key: sid_match = "finance_shark"
        elif "Skeptic" in key: sid_match = "skeptic_shark"

        p_info = INVESTOR_PERSONAS.get(sid_match, INVESTOR_PERSONAS["market_shark"])
        meta_info = SHARK_META.get(sid_match, SHARK_META["market_shark"])

        with target_col:
            html(f"""
            <div style="background:rgba(17, 20, 39, 0.75); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border:1px solid var(--border-glass); border-left:3px solid {meta_info['main_color']}; border-radius:14px; padding:1.2rem 1.35rem; margin-bottom:0.9rem; box-shadow:0 4px 16px rgba(0, 0, 0, 0.2); transition:var(--transition-fast);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.1rem;" aria-hidden="true">{p_info['avatar']}</span>
                        <strong style="color:var(--c-text-primary); font-family:'Space Grotesk',sans-serif; font-size:0.95rem;">{esc(key)}</strong>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.66rem; color:{meta_info['main_color']}; font-weight:600;">
                        {esc(meta_info['role'])}
                    </span>
                </div>
                <div style="color:var(--c-text-secondary); font-size:0.88rem; line-height:1.6;">
                    {esc(v_content)}
                </div>
            </div>
            """)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block" role="region" aria-label="Strategic Findings Header">
        <div>
            <div class="section-eyebrow">STRATEGIC INTELLIGENCE</div>
            <div class="section-title">Critical Diligence Findings</div>
        </div>
    </div>
    """)

    col_i1, col_i2, col_i3 = st.columns(3)
    insights_config = [
        ("#34d399", "#34d399", "rgba(16, 185, 129, 0.08)", "PRIMARY VENTURE STRENGTH", "🌟", res.biggest_strength),
        ("#fbbf24", "#fbbf24", "rgba(245, 158, 11, 0.08)", "STRUCTURAL WEAKNESS", "⚠️", res.biggest_weakness),
        ("#fb7185", "#fb7185", "rgba(244, 63, 94, 0.08)", "CRITICAL INVESTOR CONCERN", "🚨", res.biggest_concern)
    ]
    for col, (border, txt_c, bg_c, title, icon, body) in zip([col_i1, col_i2, col_i3], insights_config):
        with col:
            html(f"""
            <div style="background:rgba(17, 20, 39, 0.75); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border:1px solid var(--border-glass); border-top:3px solid {border}; border-radius:16px; padding:1.3rem; height:100%; box-shadow:0 4px 20px rgba(0, 0, 0, 0.2); transition:var(--transition-smooth);">
                <div style="display:flex; align-items:center; gap:0.4rem; font-family:'JetBrains Mono',monospace; font-size:0.7rem; font-weight:700; color:{txt_c}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.6rem;">
                    <span aria-hidden="true">{icon}</span>
                    <span>{title}</span>
                </div>
                <div style="color:var(--c-text-secondary); font-size:0.9rem; line-height:1.6;">
                    {esc(body)}
                </div>
            </div>
            """)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block" role="region" aria-label="Roadmap to Fundability Header">
        <div>
            <div class="section-eyebrow">ROADMAP TO FUNDABILITY</div>
            <div class="section-title">Recommended Execution Actions</div>
        </div>
    </div>
    """)

    roadmap_items_html = "".join([
        f"""<div style="display:flex; gap:0.9rem; align-items:baseline; margin-bottom:0.85rem;"><div style="font-family:'JetBrains Mono',monospace; font-size:0.76rem; font-weight:800; color:var(--c-cyan); background:rgba(34, 211, 238, 0.08); border:1px solid rgba(34, 211, 238, 0.15); padding:0.22rem 0.55rem; border-radius:8px; min-width:2rem; text-align:center;">0{i}</div><div style="color:var(--c-text-secondary); font-size:0.92rem; line-height:1.55;">{esc(action_item)}</div></div>"""
        for i, action_item in enumerate(res.top_improvements, 1)
    ])

    html(f"""
    <div style="background:rgba(17, 20, 39, 0.75); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border:1px solid var(--border-glass); border-radius:18px; padding:1.5rem 1.8rem; box-shadow:var(--shadow-card);" role="list" aria-label="Action Roadmap Items">
        {roadmap_items_html}
    </div>
    """)

    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

    c_ret_l, c_ret_m, c_ret_r = st.columns([1, 2.2, 1])
    with c_ret_m:
        if st.button("RETRY WITH REFINED DEFENSE (ROUND 2) →", use_container_width=True, type="primary"):
            st.session_state.previous_scorecard = res
            st.session_state.interrogation_history = []
            st.session_state.current_question = None
            st.session_state.turn_count = 0
            st.session_state.is_submitting = False
            st.session_state.page = "pitch_form"
            st.rerun()
