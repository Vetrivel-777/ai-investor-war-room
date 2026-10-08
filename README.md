# 🦈 AI Investor War Room

An interactive startup pitch simulator where four virtual AI investors challenge founders with adaptive questions, identify weak assumptions and contradictions, and deliver a comprehensive investment decision scorecard.

---

## 🌟 Features

- **Dark Investor-Room UI**: Premium glassmorphism dark aesthetic styled for high-stakes pitching.
- **Startup Pitch Form**: Collects 5 core inputs (Startup Name, Product Elevator Pitch, Problem Solved, Target Customer, and Business Model).
- **4 Specialized AI Investor Personas**:
  - **Market Shark** 📊 (Go-To-Market, Demand, TAM, & Competition)
  - **Tech Shark** ⚡ (Architecture, Technical Feasibility, & Moat)
  - **Finance Shark** 💰 (Pricing, Unit Economics, & Margins)
  - **Skeptic Shark** 🦈 (Unverified Claims, Logic Contradictions, & Risk Audit)
- **Adaptive Interrogation Engine**: Powered by Google Gemini (`google-genai` SDK). Questions dynamically adapt based on founder answers and detect contradictions with earlier claims.
- **Investor Scorecard**: Overall score out of 100, 6 subscores (Problem, Market, Tech, Biz Model, Competition, Moat), individual shark decisions, top strength/weakness, fatal risk concern, 3 actionable improvements, and final decision (`INVEST`, `INVEST WITH CONDITIONS`, `PASS`).
- **Score Comparison & Retry**: Pitch again to measure score improvement.

---

## 📁 Architecture

```
ai-investor-war-room/
├── app.py           # Streamlit Web App (Landing, Form, War Room, & Scorecard UI)
├── ai_engine.py     # Gemini LLM Integration & Adaptive Interrogation Engine
├── prompts.py       # Investor Shark Personas & System Prompts
├── evaluator.py     # Pitch Scorecard Dataclass & Structured Parser
├── requirements.txt # Dependencies (streamlit, python-dotenv, google-genai, pydantic)
├── .env.example     # Environment Variables Template
├── .gitignore       # Git Exclusions
└── assets/          # Static Assets & Media
```

---

## ⚙️ Environment Configuration (`.env`)

1. Copy `.env.example` to create `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your Google Gemini API key inside `.env`:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   *Note: Never commit `.env` or expose your API key.*

---

## 🚀 Installation & Local Execution

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit Application**:
   ```bash
   streamlit run app.py
   ```
   Or explicitly via Python:
   ```bash
   python -m streamlit run app.py
   ```

---

## 🔄 Interrogation & Evaluation Flow

1. **Submit Startup Pitch**: Fill in the 5 pitch memo fields.
2. **Enter War Room**: The AI investor panel initializes and generates the opening question.
3. **Adaptive Q&A Interrogation**: Answer each question. The AI engine evaluates your answer, checks for contradictions against prior statements, selects the most relevant Shark, and generates a sharp follow-up question.
4. **Final Investment Decision**: Click **Finish Interrogation** to receive your final committee scorecard, individual shark decisions, and priority improvement roadmap.

---

## 🛡️ License & Hackathon Notes

Built for hackathons. Lightweight, modular, and ready for deployment on Streamlit Community Cloud.
