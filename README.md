# DevSentry: Self-Healing SRE Agent

DevSentry is an incident response agent designed to diagnose issues, execute tests in isolated sandboxes, and automatically apply verified fixes.

## Key Features
- **Deterministic Agent Loop:** Goal -> Decide -> Tool -> Observe -> Finish
- **Sandbox Test Verification:** Real test runners evaluate runtime output exit codes.
- **Self-Correction Engine:** Automatically iterates on broken patches until assertions succeed.

## How to Run
``bash
pip install -r requirements.txt
streamlit run app.py
``
