# 🦈 AI Investor War Room — Venture Capital Interrogation Simulator

An institutional-grade, cinematic AI startup pitch interrogation platform. Four virtual venture capital partners challenge founders with adaptive stress-testing, detect contradictions across historical claims, reward strategic coachability and intellectual honesty, and synthesize a 6-axis due diligence scorecard.

---

## 🌟 Core Capabilities & Visual Design

- **Futuristic VC War Room UI**: Premium dark glassmorphism aesthetic with mesh-ambient lighting, live committee state badges, and dynamic interactive cards.
- **Strict Distinction of Founder Statements**:
  1. **True Contradictions** ⚠️: Directly conflicting assertions flagged and forensic follow-ups triggered.
  2. **Strategic Refinements** 📈: Calculated pricing, margin, or GTM parameter updates credited as coachability.
  3. **Intellectual Honesty** 🛡️: Transparent admissions of operational or technical constraints rewarded.
- **4 Specialized Investor Personas**:
  - **Market Shark** 📊 (*GTM, Customer Archetype, TAM, & Competition*)
  - **Tech Shark** ⚡ (*Architecture, Scalability Limits, Technical Moat, & IP*)
  - **Finance Shark** 💰 (*Unit Economics, CAC Payback, Pricing, & Margins*)
  - **Skeptic Shark** 🦈 (*Unverified Assumptions, Fatal Flaws, & Risk Audit*)
- **Institutional 6-Axis Scorecard**:
  - Problem Validation, Market & TAM, Technology & Moat, Unit Economics, Competition Defense, Defensibility.
- **Round 2 Re-Pitch Analytics**:
  - Live growth delta tracking (`+PTS`), comparative axis trajectory, and sentiment analysis.
- **Deterministic Zero-Downtime Fallback**:
  - Graceful fallback engine if Gemini API is temporarily unavailable or unconfigured.

---

## 📁 Repository Structure

```
ai-investor-war-room/
├── app.py                  # Streamlit Web Application (UI, State Engine, Sanitization, A11y)
├── ai_engine.py            # Gemini Client, Adaptive Prompting, Fallback Engine, Sanitized Logging
├── prompts.py              # Investor Shark Personas & System Interrogation/Evaluation Prompts
├── evaluator.py            # Typed PitchScorecard Model, Clamping, Comparison Delta Analytics
├── requirements.txt        # Python Dependencies (Streamlit, google-genai, pytest, pydantic)
├── package.json            # Node/CLI scripts for automated testing and CI evaluation
├── pytest.ini              # Pytest configuration
├── .env.example            # Environment Variable Template (GEMINI_API_KEY)
├── .gitignore              # Strict secret and credential exclusion rules
└── tests/                  # Automated Test Suite (46 Tests, 100% Pass Rate)
    ├── conftest.py         # Shared Pytest Fixtures & Test Doubles
    ├── test_core_logic.py  # Startup Validation, Statement Classification, State Transitions
    ├── test_evaluator.py   # Scorecard Parsing, Bounds Clamping, Round 2 Comparison
    ├── test_prompts.py     # Persona Specifications & Prompt Rule Verification
    ├── test_ai_engine.py   # JSON Sanitization, Error Detection, Fallbacks, Mock API
    ├── test_security.py    # XSS Protection, Secret Redaction, .env Exclusions
    ├── test_accessibility.py # WCAG Contrast, Reduced Motion, Keyboard Focus, ARIA
    └── test_e2e_simulation.py # Full Founder Lifecycle Interrogation & Re-pitch Test
```

---

## 🧪 Automated Testing Suite (46 Tests)

The repository includes a comprehensive, deterministic automated test suite with **zero external network dependency** during test runs.

### How to Run Tests

Using `pytest`:
```bash
python -m pytest
```

With verbose output:
```bash
python -m pytest -v
```

Using npm / package.json script:
```bash
npm test
```

### Test Coverage Highlights

| Test Module | Coverage Description | Status |
|:---|:---|:---:|
| `test_core_logic.py` | Startup intake validation, required fields, contradiction vs refinement classification, state transitions | **PASS** |
| `test_evaluator.py` | Score bounds clamping (0-100), scorecard parsing, decision sentiment, Round 2 comparison deltas | **PASS** |
| `test_prompts.py` | All 4 investor personas, avatars, colors, system interrogation prompt rules & evaluation guidelines | **PASS** |
| `test_ai_engine.py` | JSON parser with markdown cleanup & preambles, transient error detection, fallback engine, shark rotation, mock Gemini | **PASS** |
| `test_security.py` | HTML escaping (`esc()`) against script tags & attributes, secret redaction in error logs, `.gitignore` secret rules | **PASS** |
| `test_accessibility.py` | `@media (prefers-reduced-motion)`, `.sr-only` class, visible `:focus-visible` outlines, ARIA roles, WCAG contrast | **PASS** |
| `test_e2e_simulation.py` | End-to-end simulation from Pitch Intake -> Turn Q&A -> Refinements -> Deliberation Scorecard -> Round 2 Delta | **PASS** |

---

## 🔒 Security & Defensive Engineering

1. **Client-Side Secret Isolation**:
   - `GEMINI_API_KEY` is loaded exclusively server-side via `os.getenv()`.
   - No API keys are bundled into client HTML or browser responses.
2. **Strict Secret Protection**:
   - `.gitignore` explicitly excludes `.env`, `.env.*`, `*.key`, `*.pem`, and `.streamlit/secrets.toml`.
3. **XSS & Injection Prevention**:
   - All founder inputs and model responses interpolated into HTML components are sanitized using `esc()` (`html.escape()`).
4. **Sanitized Error Logging**:
   - `_safe_log_error()` automatically redacts sensitive parameters (`key=`, `token=`, `auth=`, `secret=`) before printing.

---

## ♿ Accessibility (WCAG 2.1 AA / AAA Compliance)

- **Semantic Landmarks**: Uses `role="region"`, `role="alert"`, `role="status"`, `role="progressbar"`, `role="article"`, and descriptive `aria-label` tags.
- **Motion Accessibility**: `@media (prefers-reduced-motion: reduce)` disables background drift, pulse animations, and scale transforms for users with motion sensitivities.
- **Visible Focus States**: Explicit `:focus-visible` outline styles with cyan indicator on all interactive elements.
- **High Contrast Ratios**: Text variables (`--c-text-primary: #f8fafc`, `--c-text-secondary: #cbd5e1`, `--c-text-muted: #94a3b8`) meet WCAG AAA requirements against dark surfaces.
- **Screen Reader Support**: `.sr-only` utility classes and ARIA live regions for AI deliberation states.

---

## ⚙️ Setup & Local Execution

1. **Clone and Configure**:
   ```bash
   cp .env.example .env
   ```
   Add your Google Gemini API key:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch Application**:
   ```bash
   python -m streamlit run app.py
   ```
   Open `http://localhost:8501` in your browser.
