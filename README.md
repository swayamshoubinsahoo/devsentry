# DevSentry: Autonomous Self-Healing SRE Agent

DevSentry is an autonomous incident response agent built for the AIC Internal Competition 2026-2027.

## Key Features
- **Deterministic Agent Loop:** Goal ➔ Decide ➔ Tool ➔ Observe ➔ Finish
- **Sandbox Test Verification:** Real test runners evaluate runtime output exit codes.
- **Self-Correction Engine:** Automatically iterates on broken patches until assertions succeed.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py