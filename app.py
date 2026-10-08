import streamlit as st
import time
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
from evaluator import parse_scorecard_json

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
# DESIGN SYSTEM — CSS (ULTIMATE BEAUTIFICATION)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── High-End Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    /* ── Root Theme Variables ── */
    :root {
        --c-navy: #0f172a;
        --c-blue: #2563eb;
        --c-indigo: #6366f1;
        --c-violet: #8b5cf6;
        --c-cyan: #06b6d4;
        --c-emerald: #10b981;
        --c-amber: #f59e0b;
        --c-gold: #c4a059;
        --c-rose: #f43f5e;
        --bg-pearl: #fcfbfa;
        --border-subtle: rgba(226, 232, 240, 0.85);
    }

    /* ── Background Atmosphere & Ambient Aura ── */
    html, body, .stApp {
        background-color: var(--bg-pearl) !important;
        color: var(--c-navy) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        overflow-x: hidden;
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: 
            radial-gradient(circle at 10% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 90% 20%, rgba(6, 182, 212, 0.07) 0%, transparent 40%),
            radial-gradient(circle at 50% 60%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 85% 85%, rgba(245, 158, 11, 0.05) 0%, transparent 40%),
            linear-gradient(rgba(15, 23, 42, 0.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15, 23, 42, 0.018) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        pointer-events: none;
        z-index: 0;
        animation: ambientDrift 25s ease-in-out infinite alternate;
    }

    @keyframes ambientDrift {
        0% { transform: scale(1) translateY(0); }
        50% { transform: scale(1.015) translateY(-6px); }
        100% { transform: scale(1) translateY(0); }
    }

    #MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }

    .block-container {
        padding: 1.2rem 2.2rem 3.5rem 2.2rem !important;
        max-width: 1280px !important;
        position: relative;
        z-index: 1;
    }

    /* ── Typography Scale ── */
    h1, h2, h3, h4, h5, h6 {
        color: var(--c-navy) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
    }
    p, span, div, li {
        color: #1e293b;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── Keyframe Animations ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes scalePop {
        from { opacity: 0; transform: scale(0.97); }
        to   { opacity: 1; transform: scale(1); }
    }
    @keyframes shimmerBar {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes pulseAura {
        0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
        50%      { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
    }
    @keyframes pulseGreen {
        0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5); }
        50%      { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    }
    @keyframes alertGlow {
        0%, 100% { box-shadow: 0 4px 20px -2px rgba(239, 68, 68, 0.15), 0 0 0 1px rgba(239, 68, 68, 0.4); }
        50%      { box-shadow: 0 8px 30px rgba(239, 68, 68, 0.28), 0 0 0 2px rgba(239, 68, 68, 0.7); }
    }

    .anim-fade { animation: fadeSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .anim-scale { animation: scalePop 0.45s cubic-bezier(0.16, 1, 0.3, 1) both; }

    /* ── Top Navigation Shell ── */
    .shell-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 0.75rem 1.35rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px -2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02);
    }
    .shell-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .shell-logo-badge {
        width: 36px; height: 36px;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4f46e5 100%);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-size: 1.15rem;
        font-weight: 900;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        border: 1px solid rgba(165, 180, 252, 0.4);
    }
    .shell-title-text {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 900;
        color: var(--c-navy) !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .shell-sub-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        color: var(--c-indigo) !important;
        text-transform: uppercase;
    }
    .shell-stepper {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .shell-step-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.74rem;
        font-weight: 700;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }
    .shell-step-item.is-active {
        color: #ffffff !important;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        box-shadow: 0 2px 8px rgba(30, 27, 75, 0.2);
    }
    .shell-step-item.is-done {
        color: #475569;
        background: #f1f5f9;
    }
    .shell-step-item .step-num {
        color: var(--c-cyan);
        font-weight: 800;
    }
    .shell-step-item.is-active .step-num {
        color: #38bdf8;
    }
    .shell-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        background: #ecfdf5;
        color: #065f46 !important;
        border: 1px solid #a7f3d0;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.12);
    }
    .pulse-dot-green {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #10b981;
        animation: pulseGreen 2s infinite;
    }
    .pulse-dot-amber {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #f59e0b;
        box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);
    }

    /* ── Hero Section (The Wow Moment) ── */
    .hero-panel {
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-subtle);
        border-radius: 24px;
        padding: 3rem 2.2rem 2.2rem;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 48px -12px rgba(15, 23, 42, 0.07), 0 0 0 1px rgba(255, 255, 255, 0.8);
    }
    .hero-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 35%, #06b6d4 70%, #10b981 100%);
        background-size: 200% auto;
        animation: shimmerBar 4s linear infinite;
    }
    .hero-tag-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        color: #4338ca !important;
        background: linear-gradient(135deg, rgba(238, 242, 255, 0.95) 0%, rgba(245, 243, 255, 0.95) 100%);
        border: 1px solid rgba(199, 210, 254, 0.85);
        padding: 0.38rem 1rem;
        border-radius: 30px;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.12);
    }
    .hero-title-main {
        font-family: 'Outfit', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.04em !important;
        line-height: 1.05 !important;
        margin: 0 0 0.85rem 0 !important;
    }
    .hero-title-gradient {
        background: linear-gradient(135deg, #1e1b4b 0%, #2563eb 30%, #7c3aed 65%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 4px 18px rgba(99, 102, 241, 0.18));
    }
    .hero-tagline {
        font-size: 1.25rem;
        font-weight: 600;
        color: #334155 !important;
        margin-bottom: 0.75rem;
        letter-spacing: -0.015em;
    }
    .hero-explanation {
        font-size: 0.96rem;
        color: #64748b !important;
        max-width: 660px;
        margin: 0 auto 1.8rem;
        line-height: 1.65;
    }
    .hero-pipeline-strip {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.2rem;
        background: rgba(248, 250, 252, 0.9);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.65rem 1.4rem;
        max-width: 680px;
        margin: 0 auto;
    }
    .pipeline-node {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        font-weight: 700;
        color: #334155;
    }
    .pipeline-node .num {
        color: var(--c-indigo);
        font-weight: 800;
    }
    .pipeline-divider {
        color: #cbd5e1;
        font-size: 0.85rem;
    }

    /* ── Section Titles ── */
    .section-header-block {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 1.1rem;
        padding: 0 0.2rem;
    }
    .section-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 800;
        color: var(--c-indigo) !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .section-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.45rem;
        font-weight: 800;
        color: var(--c-navy) !important;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .section-badge-info {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        background: #f1f5f9;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
    }

    /* ── Investor Persona Cards ── */
    .investor-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
        padding: 1.35rem 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
    }
    .investor-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--inv-accent-grad, #3b82f6);
        transition: height 0.2s ease;
    }
    .investor-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 36px -8px var(--inv-shadow-glow, rgba(15, 23, 42, 0.1)), 0 0 0 1px var(--inv-border-glow, #cbd5e1);
    }
    .investor-card:hover::before {
        height: 6px;
    }
    .investor-card.is-interrogating {
        border: 2px solid var(--inv-main-color, #6366f1) !important;
        background: linear-gradient(180deg, #ffffff 0%, #faf8ff 100%);
        box-shadow: 0 12px 32px var(--inv-shadow-glow, rgba(99, 102, 241, 0.2)) !important;
        animation: pulseAura 2.5s infinite;
    }
    .investor-top-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
    }
    .investor-avatar-box {
        width: 44px; height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        background: var(--inv-bg-light, #eff6ff);
        border: 1px solid var(--inv-border-light, #bfdbfe);
        box-shadow: 0 2px 8px var(--inv-shadow-soft, rgba(0,0,0,0.03));
        transition: transform 0.25s ease;
    }
    .investor-card:hover .investor-avatar-box {
        transform: scale(1.1) rotate(2deg);
    }
    .investor-id-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 800;
        padding: 0.22rem 0.55rem;
        border-radius: 6px;
        background: #f1f5f9;
        color: #475569;
        letter-spacing: 0.05em;
    }
    .investor-name-heading {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--c-navy) !important;
        letter-spacing: -0.01em;
        margin-bottom: 0.15rem;
    }
    .investor-quote-personality {
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--inv-main-color, #2563eb) !important;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    .investor-role-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
    }
    .investor-description-body {
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.5;
        flex-grow: 1;
        margin-bottom: 0.85rem;
    }
    .pill-tag {
        display: inline-block;
        font-size: 0.66rem;
        font-weight: 700;
        background: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }

    /* ── Feature Cards ── */
    .feature-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.35rem;
        height: 100%;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px -4px rgba(15, 23, 42, 0.07);
    }
    .feature-icon-bubble {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }

    /* ── Form Inputs & Textarea ── */
    label, .stTextInput label, .stTextArea label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: var(--c-navy) !important;
        font-weight: 800 !important;
        font-size: 0.74rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        font-family: 'JetBrains Mono', monospace !important;
        margin-bottom: 0.35rem !important;
    }
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stForm"] input,
    [data-testid="stForm"] textarea {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #d8dbe0 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 0.75rem 1rem !important;
        line-height: 1.55 !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
    }
    .stTextInput input:hover,
    .stTextArea textarea:hover {
        border-color: #94a3b8 !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15) !important;
        background: #fbfdff !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    ::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
        font-weight: 400 !important;
    }

    /* ── Button Hierarchy & Interactions ── */
    button[kind="primary"],
    .stButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"],
    div.stFormSubmitButton > button[kind="primary"],
    div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 35%, #312e81 70%, #2563eb 100%) !important;
        background-size: 200% auto !important;
        color: #ffffff !important;
        border: 1px solid rgba(199, 210, 254, 0.45) !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.94rem !important;
        letter-spacing: 0.03em !important;
        padding: 0.75rem 1.6rem !important;
        box-shadow: 0 4px 18px rgba(49, 46, 129, 0.35), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
    }
    button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover,
    div.stFormSubmitButton > button:first-child:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 28px rgba(79, 70, 229, 0.5), 0 0 18px rgba(99, 102, 241, 0.35) !important;
        border-color: rgba(165, 180, 252, 0.9) !important;
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
        font-weight: 800 !important;
    }

    button[kind="secondary"],
    .stButton > button[kind="secondary"],
    [data-testid="stBaseButton-secondary"],
    div.stFormSubmitButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: var(--c-navy) !important;
        border: 1.5px solid #d8dbe0 !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.7rem 1.4rem !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover {
        border-color: #6366f1 !important;
        background: #f8fafc !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.12) !important;
    }
    button[kind="secondary"] p,
    button[kind="secondary"] span,
    [data-testid="stBaseButton-secondary"] p,
    [data-testid="stBaseButton-secondary"] span {
        color: var(--c-navy) !important;
        font-weight: 700 !important;
    }

    /* ── War Room Arena ── */
    .wr-banner-header {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.1rem 1.6rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
    }
    .wr-stats-group {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    .wr-stat-cell {
        display: flex;
        flex-direction: column;
    }
    .wr-stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 800;
        color: #94a3b8;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .wr-stat-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--c-navy);
    }

    .question-stage-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px -4px rgba(15, 23, 42, 0.06);
        position: relative;
        overflow: hidden;
    }
    .question-stage-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 5px;
        background: var(--q-accent-grad, #3b82f6);
    }
    .question-top-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .question-investor-info {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .question-quote-box {
        font-size: 1.26rem;
        font-weight: 600;
        color: #0f172a !important;
        line-height: 1.65;
        letter-spacing: -0.015em;
        background: #fbfbfe;
        border: 1px solid #eef2ff;
        padding: 1.5rem 1.6rem;
        border-radius: 14px;
    }

    /* ── Contradiction Callout ── */
    .contradiction-callout {
        background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
        border: 1.5px solid #fca5a5;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.25rem;
        animation: alertGlow 2.5s infinite;
    }
    .contradiction-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 800;
        color: #b91c1c;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .contradiction-body {
        font-size: 0.92rem;
        color: #991b1b;
        line-height: 1.55;
        font-weight: 500;
    }

    /* ── Transcript Timeline ── */
    .timeline-node-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .timeline-q-bubble {
        background: #f8fafc;
        border-left: 3px solid #6366f1;
        padding: 0.85rem 1.1rem;
        border-radius: 8px;
        font-size: 0.92rem;
        color: #1e293b;
        margin-bottom: 0.6rem;
        line-height: 1.55;
    }
    .timeline-a-bubble {
        background: #faf8f5;
        border-left: 3px solid #c4a059;
        padding: 0.85rem 1.1rem;
        border-radius: 8px;
        font-size: 0.92rem;
        color: #0f172a;
        line-height: 1.55;
    }

    /* ── Scorecard & Diligence Metrics ── */
    .verdict-hero-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.8rem 2rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 8px 32px -4px rgba(15, 23, 42, 0.06);
        position: relative;
        overflow: hidden;
    }
    .verdict-hero-card.invest-pass {
        border: 2px solid #ef4444;
        background: linear-gradient(135deg, #ffffff 0%, #fef2f2 100%);
    }
    .verdict-hero-card.invest-cond {
        border: 2px solid #f59e0b;
        background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);
    }
    .verdict-hero-card.invest-yes {
        border: 2px solid #10b981;
        background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 100%);
    }
    .verdict-stamp-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .verdict-title-text {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .verdict-subtext {
        font-size: 0.95rem;
        line-height: 1.55;
    }

    .score-gauge-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 32px -4px rgba(15, 23, 42, 0.06);
    }

    .dim-metric-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .dim-metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }
    .dim-metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .dim-metric-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 800;
        color: #64748b;
        letter-spacing: 0.08em;
    }
    .dim-metric-num {
        font-family: 'Outfit', sans-serif;
        font-size: 1.85rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    .dim-metric-bar {
        height: 6px;
        background: #f1f5f9;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.4rem;
    }
    .dim-metric-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s ease;
    }
    .dim-metric-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.06em;
    }

    .round-delta-strip {
        background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
        border: 1.5px solid #86efac;
        border-radius: 16px;
        padding: 1.1rem 1.8rem;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);
    }
    .round-delta-cell {
        text-align: center;
    }
    .round-delta-lbl {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        color: #047857;
    }
    .round-delta-val {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 900;
        color: var(--c-navy);
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
        "main_color": "#06b6d4",
        "grad": "linear-gradient(90deg, #06b6d4, #10b981)",
        "bg_light": "#ecfeff",
        "border_light": "#a5f3fc",
        "shadow_glow": "rgba(6, 182, 212, 0.22)",
        "quote": '"Does anyone actually want this?"',
        "role": "Market Intelligence & Demand",
        "specs": "TAM · ICP · Distribution Velocity",
        "desc": "Challenges go-to-market speed, ICP definition, distribution channels, and addressable market realism.",
        "pills": ["Target Customer Profile", "TAM / SAM / SOM"]
    },
    "tech_shark": {
        "main_color": "#3b82f6",
        "grad": "linear-gradient(90deg, #3b82f6, #6366f1)",
        "bg_light": "#eff6ff",
        "border_light": "#bfdbfe",
        "shadow_glow": "rgba(59, 130, 246, 0.22)",
        "quote": '"Can you actually build and scale it?"',
        "role": "Deep Tech Architecture & Scalability",
        "specs": "Architecture · Moat · Proprietary IP",
        "desc": "Audits infrastructure feasibility, tech debt, defensible IP barriers, and distributed scale limits.",
        "pills": ["Core Tech Stack", "Defensible Moat"]
    },
    "finance_shark": {
        "main_color": "#f59e0b",
        "grad": "linear-gradient(90deg, #f59e0b, #d97706)",
        "bg_light": "#fffbeb",
        "border_light": "#fde68a",
        "shadow_glow": "rgba(245, 158, 11, 0.22)",
        "quote": '"Will this generate venture returns?"',
        "role": "Financial Discipline & Unit Economics",
        "specs": "Payback · Margins · Burn Multiple",
        "desc": "Dissects monetization mechanics, gross margins, CAC payback cycles, and path to venture profitability.",
        "pills": ["Unit Economics", "CAC / LTV Payback"]
    },
    "skeptic_shark": {
        "main_color": "#f43f5e",
        "grad": "linear-gradient(90deg, #f43f5e, #a855f7)",
        "bg_light": "#fff1f2",
        "border_light": "#fecdd3",
        "shadow_glow": "rgba(244, 63, 94, 0.22)",
        "quote": '"What are you not telling us?"',
        "role": "Risk Auditor & Contradiction Police",
        "specs": "Assumptions · Contradictions · Logic Flaws",
        "desc": "Forensically probes unverified claims, logical fallacies, and discrepancies between past statements.",
        "pills": ["Contradiction Matrix", "Execution Blindspots"]
    }
}

# ═══════════════════════════════════════════════════════════
# REUSABLE PRESENTATION COMPONENTS
# ═══════════════════════════════════════════════════════════
def render_shell():
    pg = st.session_state.page
    has_key = bool(get_api_key())
    status_label = "INVESTMENT ENGINE ONLINE" if has_key else "DETERMINISTIC BACKUP ACTIVE"
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
            <span style="color:#cbd5e1; font-size:.8rem;">→</span>
            <div class="shell-step-item {s2}"><span class="step-num">02</span> WAR ROOM</div>
            <span style="color:#cbd5e1; font-size:.8rem;">→</span>
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
    <div style="background:#fffbeb; border:1px solid #fde68a; border-left:4px solid #f59e0b; border-radius:12px; padding:0.9rem 1.25rem; margin-bottom:1.5rem;">
        <div style="font-family:'JetBrains Mono',monospace; font-weight:800; color:#b45309; font-size:0.75rem; letter-spacing:0.06em; margin-bottom:0.2rem;">
            ⚠ GEMINI API KEY RUNNING IN BACKUP MODE
        </div>
        <div style="color:#78350f; font-size:0.86rem; line-height:1.45;">
            Operating on deterministic backup question logic. Configure <code>GEMINI_API_KEY</code> in <code>.env</code> for live multi-turn Gemini 2.5 Flash intelligence.
        </div>
    </div>
    """)

def render_svg_score_ring(score: int) -> str:
    circumference = 301.59
    offset = circumference * (1.0 - max(0, min(100, score)) / 100.0)
    
    if score >= 80:
        c1, c2 = "#10b981", "#06b6d4"
        badge_txt = "HIGH CONVICTION"
        badge_bg = "#ecfdf5"
        badge_clr = "#065f46"
    elif score >= 70:
        c1, c2 = "#f59e0b", "#c4a059"
        badge_txt = "CONDITIONAL"
        badge_bg = "#fffbeb"
        badge_clr = "#92400e"
    else:
        c1, c2 = "#ef4444", "#f43f5e"
        badge_txt = "NEEDS WORK"
        badge_bg = "#fef2f2"
        badge_clr = "#991b1b"

    return f"""
    <div class="score-gauge-card">
        <svg width="150" height="150" viewBox="0 0 120 120">
            <defs>
                <linearGradient id="scoreRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="{c1}" />
                    <stop offset="100%" stop-color="{c2}" />
                </linearGradient>
                <filter id="ringGlow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>
            <circle cx="60" cy="60" r="48" fill="none" stroke="#f1f5f9" stroke-width="8" />
            <circle cx="60" cy="60" r="48" fill="none" stroke="url(#scoreRingGrad)" stroke-width="8"
                    stroke-dasharray="301.59" stroke-dashoffset="{offset:.2f}"
                    stroke-linecap="round" transform="rotate(-90 60 60)" filter="url(#ringGlow)" />
            <text x="60" y="56" text-anchor="middle" font-family="'Outfit', sans-serif" font-size="28" font-weight="900" fill="#0f172a">{score}</text>
            <text x="60" y="74" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="700" fill="#64748b">/ 100</text>
        </svg>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; font-weight:800; letter-spacing:0.1em; color:#64748b; margin-top:0.4rem;">
            SYNDICATE COMPOSITE
        </div>
        <div style="background:{badge_bg}; color:{badge_clr}; font-family:'JetBrains Mono',monospace; font-size:0.66rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:12px; margin-top:0.35rem;">
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
            AI INVESTOR<br>
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
            <div class="investor-card" style="
                --inv-accent-grad: {meta['grad']};
                --inv-main-color: {meta['main_color']};
                --inv-bg-light: {meta['bg_light']};
                --inv-border-light: {meta['border_light']};
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
                <div style="font-size:0.75rem; font-weight:700; color:{meta['main_color']}; margin-bottom:0.5rem; font-family:'JetBrains Mono',monospace;">
                    {meta['specs']}
                </div>
                <div class="investor-description-body">{meta['desc']}</div>
                <div>{pills_html}</div>
            </div>
            """)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    feature_data = [
        ("⚡", "#eff6ff", "#3b82f6", "Dynamic Adaptive Questions", "Each follow-up question is synthesized in real-time from your exact defense, probing weaknesses and avoiding generic scripted queries."),
        ("🔍", "#fef2f2", "#ef4444", "Contradiction Matrix Engine", "Identifies discrepancies when your live answers diverge from earlier claims or pitch memo metrics, forcing intellectual consistency."),
        ("🏆", "#ecfdf5", "#10b981", "Institutional Due Diligence", "6-axis weighted scoring, partner syndicate vote consensus, top risks breakdown, and prioritized operational roadmap.")
    ]
    for col, (icon, bg, clr, title, body) in zip([f1, f2, f3], feature_data):
        with col:
            html(f"""
            <div class="feature-card">
                <div class="feature-icon-bubble" style="background:{bg}; color:{clr};">{icon}</div>
                <div style="font-family:'Outfit',sans-serif; font-weight:800; font-size:1.05rem; color:#0f172a; margin-bottom:0.35rem;">{title}</div>
                <div style="font-size:0.86rem; color:#64748b; line-height:1.55;">{body}</div>
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
    <div style="background:#ffffff; border:1px solid rgba(226, 232, 240, 0.85); border-radius:20px; padding:2rem 2.2rem 1.6rem; margin-bottom:1.5rem; box-shadow:0 8px 30px -4px rgba(15, 23, 42, 0.04); position:relative; overflow:hidden;">
        <div style="position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, #6366f1, #06b6d4);"></div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="section-eyebrow">STAGE 01 : VENTURE INTAKE</div>
                <h2 style="font-size:1.85rem; margin:0.15rem 0 0.4rem;">Confidential Pitch Memo</h2>
                <div style="color:#64748b; font-size:0.92rem; max-width:680px; line-height:1.55;">
                    Provide your venture thesis below. The 4 investor partners will analyze every parameter to construct customized opening challenges.
                </div>
            </div>
            <div style="text-align:right; font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#94a3b8; background:#f8fafc; border:1px solid #e2e8f0; padding:0.5rem 0.85rem; border-radius:10px;">
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
                <span class="wr-stat-value">{p['startup_name']}</span>
            </div>
            <div class="wr-stat-cell">
                <span class="wr-stat-label">SESSION PHASE</span>
                <span class="wr-stat-value" style="color:var(--c-indigo);">ROUND 0{round_num} INTERROGATION</span>
            </div>
            <div class="wr-stat-cell">
                <span class="wr-stat-label">CHALLENGES DEFENDED</span>
                <span class="wr-stat-value">{len(st.session_state.interrogation_history)} TURNS</span>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; background:#ecfdf5; border:1px solid #a7f3d0; padding:0.4rem 0.9rem; border-radius:30px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:800; color:#065f46;">
            <span class="pulse-dot-green"></span>
            <span>COMMITTEE IN SESSION</span>
        </div>
    </div>
    """)

    if not get_api_key():
        render_api_warning()

    if st.session_state.current_question is None and len(st.session_state.interrogation_history) == 0:
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
            status_chip = f"""<span style="font-family:'JetBrains Mono',monospace; font-size:0.64rem; font-weight:800; background:{meta['bg_light']}; color:{meta['main_color']}; border:1px solid {meta['border_light']}; padding:0.2rem 0.5rem; border-radius:10px;">● ACTIVE</span>""" if is_active else """<span style="font-family:'JetBrains Mono',monospace; font-size:0.64rem; font-weight:700; color:#94a3b8; background:#f8fafc; padding:0.2rem 0.5rem; border-radius:10px;">STANDBY</span>"""

            html(f"""
            <div class="investor-card {active_cls}" style="margin-bottom:0.75rem; padding:0.95rem 1.1rem; --inv-accent-grad:{meta['grad']}; --inv-main-color:{meta['main_color']}; --inv-bg-light:{meta['bg_light']}; --inv-border-light:{meta['border_light']}; --inv-shadow-glow:{meta['shadow_glow']}; --inv-border-glow:{meta['main_color']};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.15rem;">{s['avatar']}</span>
                        <strong style="font-family:'Outfit',sans-serif; font-size:0.95rem; color:#0f172a;">{s['name']}</strong>
                    </div>
                    {status_chip}
                </div>
                <div style="font-size:0.72rem; color:{meta['main_color']}; font-weight:700; font-style:italic;">
                    {meta['quote']}
                </div>
            </div>
            """)

        with st.expander("📋 Venture Memo Details", expanded=False):
            html(f"""
            <div style="font-size:0.84rem; color:#334155; line-height:1.55;">
                <p><strong>Venture:</strong> {p['startup_name']}</p>
                <p><strong>Product:</strong> {p['building']}</p>
                <p><strong>ICP:</strong> {p['target_customer']}</p>
                <p><strong>Problem:</strong> {p['problem']}</p>
                <p><strong>Model:</strong> {p['business_model']}</p>
            </div>
            """)

    with col_arena:
        if st.session_state.current_question:
            cq = st.session_state.current_question
            sid = cq["shark_id"]
            persona = INVESTOR_PERSONAS.get(sid, INVESTOR_PERSONAS["market_shark"])
            meta = SHARK_META.get(sid, SHARK_META["market_shark"])
            q_num = len(st.session_state.interrogation_history) + 1

            fallback_html = """<div style="background:#fffdfa; border:1px solid #fde68a; color:#b45309; padding:0.4rem 0.85rem; border-radius:8px; font-size:0.76rem; font-weight:700; font-family:'JetBrains Mono',monospace; margin-bottom:1rem;">⚡ AI Traffic Congested — Deterministic Fallback Logic Active</div>""" if cq.get("is_fallback") else ""

            contra_html = f"""<div class="contradiction-callout anim-fade"><div class="contradiction-header"><span>⚠️</span><span>CONTRADICTION DETECTED BY AI AUDITOR</span></div><div class="contradiction-body">{cq['contradiction_warning']}</div></div>""" if cq.get("contradiction_warning") else ""

            html(f"""
            <div class="question-stage-card anim-scale" style="--q-accent-grad: {meta['grad']};">
                {fallback_html}
                {contra_html}
                <div class="question-top-meta">
                    <div class="question-investor-info">
                        <div class="investor-avatar-box" style="background:{meta['bg_light']}; border-color:{meta['border_light']};">
                            {persona['avatar']}
                        </div>
                        <div>
                            <div style="font-family:'Outfit',sans-serif; font-size:1.15rem; font-weight:800; color:{meta['main_color']};">
                                {cq['shark_name']}
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#64748b; font-weight:700;">
                                {meta['role']}
                            </div>
                        </div>
                    </div>
                    <div style="background:#f1f5f9; color:#0f172a; font-family:'JetBrains Mono',monospace; font-weight:800; font-size:0.76rem; padding:0.3rem 0.75rem; border-radius:12px;">
                        QUESTION 0{q_num}
                    </div>
                </div>
                <div class="question-quote-box">
                    "{cq['question']}"
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

                html(f"""
                <div class="timeline-node-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span style="font-family:'JetBrains Mono',monospace; font-size:0.74rem; font-weight:800; background:#f1f5f9; padding:0.2rem 0.5rem; border-radius:6px;">Q0{turn_seq}</span>
                            <span style="font-size:1.1rem;">{p_item['avatar']}</span>
                            <strong style="color:#0f172a; font-family:'Outfit',sans-serif; font-size:0.95rem;">{turn['shark_name']}</strong>
                        </div>
                        <span style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:{meta_item['main_color']}; font-weight:700;">
                            {meta_item['role']}
                        </span>
                    </div>
                    <div class="timeline-q-bubble">
                        <strong>CHALLENGE:</strong> {turn['question']}
                    </div>
                    <div class="timeline-a-bubble">
                        <strong>DEFENSE:</strong> {turn['answer']}
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
    <div class="hero-panel anim-scale" style="padding:2.2rem 2.2rem 1.8rem; margin-bottom:1.5rem;">
        <div class="hero-tag-badge">
            <span>✦</span>
            <span>INVESTMENT COMMITTEE DUE DILIGENCE REPORT</span>
            <span>✦</span>
        </div>
        <h1 class="hero-title-main" style="font-size:2.8rem !important; margin-bottom:0.4rem !important;">
            {p['startup_name']}
        </h1>
        <div class="hero-tagline" style="font-size:1.15rem; margin-bottom:0;">
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
        <div style="background:#fffdfa; border:1px solid #fde68a; color:#b45309; text-align:center; padding:0.45rem 1rem; border-radius:8px; font-size:0.78rem; font-weight:700; font-family:'JetBrains Mono',monospace; margin-bottom:1.25rem;">
            ⚡ Scorecard assembled via deterministic backup due-diligence evaluator
        </div>
        """)

    if st.session_state.previous_scorecard:
        prev_score = st.session_state.previous_scorecard.overall_score
        curr_score = res.overall_score
        delta = curr_score - prev_score
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        delta_color = "#10b981" if delta >= 0 else "#ef4444"
        html(f"""
        <div class="round-delta-strip anim-fade">
            <div class="round-delta-cell">
                <div class="round-delta-lbl">ROUND 01 SCORE</div>
                <div class="round-delta-val">{prev_score} <span style="font-size:.9rem; color:#94a3b8;">/100</span></div>
            </div>
            <div style="font-size:1.5rem; color:#94a3b8;">→</div>
            <div class="round-delta-cell">
                <div class="round-delta-lbl">ROUND 02 SCORE</div>
                <div class="round-delta-val">{curr_score} <span style="font-size:.9rem; color:#94a3b8;">/100</span></div>
            </div>
            <div style="font-size:1.5rem; color:#94a3b8;">→</div>
            <div class="round-delta-cell">
                <div class="round-delta-lbl">GROWTH DELTA</div>
                <div class="round-delta-val" style="color:{delta_color};">{delta_str} PTS 🚀</div>
            </div>
        </div>
        """)

    verdict_text = res.final_decision.upper()
    col_verdict, col_gauge = st.columns([2.2, 1.1])

    with col_verdict:
        if "INVEST WITH CONDITIONS" in verdict_text or "CONDITIONAL" in verdict_text:
            html("""
            <div class="verdict-hero-card invest-cond anim-fade">
                <div class="verdict-stamp-badge" style="color:#b45309;">SYNDICATE VERDICT : CONDITIONAL OFFER</div>
                <div class="verdict-title-text" style="color:#92400e;">⚠️ CONDITIONAL TERM SHEET</div>
                <div class="verdict-subtext" style="color:#78350f;">
                    The investment committee extends a conditional term sheet. Syndicate funding is contingent on successfully mitigating key customer acquisition and technical scalability risks highlighted during interrogation.
                </div>
            </div>
            """)
        elif "INVEST" in verdict_text:
            html("""
            <div class="verdict-hero-card invest-yes anim-fade">
                <div class="verdict-stamp-badge" style="color:#047857;">SYNDICATE VERDICT : UNANIMOUS OFFER</div>
                <div class="verdict-title-text" style="color:#065f46;">🎉 TERM SHEET EXTENDED</div>
                <div class="verdict-subtext" style="color:#064e3b;">
                    The committee reached consensus to issue an institutional term sheet. Founder demonstrated exceptional conviction, defensibility, and command of core unit economics across all 4 partner interrogations.
                </div>
            </div>
            """)
        else:
            html("""
            <div class="verdict-hero-card invest-pass anim-fade">
                <div class="verdict-stamp-badge" style="color:#b91c1c;">SYNDICATE VERDICT : COMMITTEE PASS</div>
                <div class="verdict-title-text" style="color:#991b1b;">❌ COMMITTEE PASS</div>
                <div class="verdict-subtext" style="color:#7f1d1d;">
                    The syndicate declined to issue a term sheet at this time. Structural market defensibility concerns, margin headwinds, and unresolved assumptions require further customer validation before funding.
                </div>
            </div>
            """)

    with col_gauge:
        html(render_svg_score_ring(res.overall_score))

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block">
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
            bar_clr = "#10b981"
            tag_clr = "#065f46"
            status_text = "STRONG"
        elif score_val >= 70:
            bar_clr = "#f59e0b"
            tag_clr = "#92400e"
            status_text = "VIABLE"
        else:
            bar_clr = "#ef4444"
            tag_clr = "#991b1b"
            status_text = "EXPOSED"

        with cols_dim[i]:
            html(f"""
            <div class="dim-metric-card">
                <div>
                    <div class="dim-metric-header">
                        <span class="dim-metric-name">{name}</span>
                        <span>{icon}</span>
                    </div>
                    <div class="dim-metric-num" style="color:{bar_clr};">
                        {score_val}
                    </div>
                </div>
                <div>
                    <div class="dim-metric-bar">
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
    <div class="section-header-block">
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
            <div style="background:#ffffff; border:1px solid rgba(226, 232, 240, 0.85); border-left:4px solid {meta_info['main_color']}; border-radius:14px; padding:1.2rem 1.35rem; margin-bottom:1rem; box-shadow:0 2px 10px rgba(15, 23, 42, 0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.15rem;">{p_info['avatar']}</span>
                        <strong style="color:#0f172a; font-family:'Outfit',sans-serif; font-size:1rem;">{key}</strong>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:{meta_info['main_color']}; font-weight:700;">
                        {meta_info['role']}
                    </span>
                </div>
                <div style="color:#334155; font-size:0.9rem; line-height:1.6;">
                    {v_content}
                </div>
            </div>
            """)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block">
        <div>
            <div class="section-eyebrow">STRATEGIC INTELLIGENCE</div>
            <div class="section-title">Critical Diligence Findings</div>
        </div>
    </div>
    """)

    col_i1, col_i2, col_i3 = st.columns(3)
    insights_config = [
        ("#10b981", "#047857", "#ecfdf5", "PRIMARY VENTURE STRENGTH", "🌟", res.biggest_strength),
        ("#f59e0b", "#b45309", "#fffbeb", "STRUCTURAL WEAKNESS", "⚠️", res.biggest_weakness),
        ("#ef4444", "#b91c1c", "#fef2f2", "CRITICAL INVESTOR CONCERN", "🚨", res.biggest_concern)
    ]
    for col, (border, txt_c, bg_c, title, icon, body) in zip([col_i1, col_i2, col_i3], insights_config):
        with col:
            html(f"""
            <div style="background:#ffffff; border:1px solid rgba(226, 232, 240, 0.85); border-top:4px solid {border}; border-radius:16px; padding:1.35rem; height:100%; box-shadow:0 4px 16px -2px rgba(15, 23, 42, 0.04);">
                <div style="display:flex; align-items:center; gap:0.4rem; font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:800; color:{txt_c}; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.6rem;">
                    <span>{icon}</span>
                    <span>{title}</span>
                </div>
                <div style="color:#0f172a; font-size:0.92rem; line-height:1.55;">
                    {body}
                </div>
            </div>
            """)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    html("""
    <div class="section-header-block">
        <div>
            <div class="section-eyebrow">ROADMAP TO FUNDABILITY</div>
            <div class="section-title">Recommended Execution Actions</div>
        </div>
    </div>
    """)

    roadmap_items_html = "".join([
        f"""<div style="display:flex; gap:0.9rem; align-items:baseline; margin-bottom:0.85rem;"><div style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:900; color:var(--c-indigo); background:#eef2ff; border:1px solid #c7d2fe; padding:0.25rem 0.6rem; border-radius:8px; min-width:2.2rem; text-align:center;">0{i}</div><div style="color:#1e293b; font-size:0.94rem; line-height:1.55;">{action_item}</div></div>"""
        for i, action_item in enumerate(res.top_improvements, 1)
    ])

    html(f"""
    <div style="background:#ffffff; border:1px solid rgba(226, 232, 240, 0.85); border-radius:18px; padding:1.5rem 1.8rem; box-shadow:0 4px 20px -2px rgba(15, 23, 42, 0.04);">
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
