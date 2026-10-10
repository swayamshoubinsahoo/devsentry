import streamlit as st
import os
from agent import build_agent_graph

st.set_page_config(page_title="DevSentry AI", page_icon="🛡️", layout="wide")

with st.sidebar:
    st.title("⚙️ Credentials")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API Key")

st.title("🛡️ DevSentry: Autonomous Self-Healing SRE")
st.caption("Goal ➔ Decide ➔ Tool ➔ Observe ➔ Finish")

# Scenario library
SCENARIOS = {
    "Checkout Bug (ZeroDivisionError)": {
        "alert": "CRITICAL ALERT: HTTP 500 in Checkout Engine. ZeroDivisionError when applying a 0-item coupon.",
        "file": "discount_service.py",
        "test_file": "test_discount.py",
        "broken_code": (
            "def calculate_discount(total_amount, items_count):\n"
            "    # Bug: Division by zero when items_count == 0\n"
            "    discount_ratio = 10 / items_count\n"
            "    return total_amount - (total_amount * discount_ratio)\n"
        ),
        "test_code": (
            "from discount_service import calculate_discount\n"
            "assert calculate_discount(100, 2) == 100 - (100 * 5)\n"
            "assert calculate_discount(50, 0) == 50\n"
            "print('ALL_TESTS_PASSED')\n"
        )
    },
    "Payment Gateway (KeyError / Crash)": {
        "alert": "PRODUCTION P1: KeyError 'tax_rate' in payment processor when checking out guest orders.",
        "file": "payment_service.py",
        "test_file": "test_payment.py",
        "broken_code": (
            "def process_transaction(amount, meta):\n"
            "    # Bug: Crashes if 'tax_rate' is missing for guest users\n"
            "    tax = amount * meta['tax_rate']\n"
            "    return amount + tax\n"
        ),
        "test_code": (
            "from payment_service import process_transaction\n"
            "assert process_transaction(100, {'tax_rate': 0.1}) == 110.0\n"
            "assert process_transaction(100, {}) == 100.0\n"
            "print('ALL_TESTS_PASSED')\n"
        )
    }
}

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Incident Alert Payload")
    selected_scenario = st.selectbox("Choose Outage Scenario", list(SCENARIOS.keys()), index=1)
    current_data = SCENARIOS[selected_scenario]
    
    incident_text = st.text_area("Simulated Alert Payload", value=current_data["alert"], height=90)
    target_file = st.text_input("Vulnerable File Path", value=current_data["file"])
    test_file = st.text_input("Test Suite Path", value=current_data["test_file"])
    
    if st.button("🔥 Simulate Outage & Launch Agent", type="primary"):
        if not gemini_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar!")
        else:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(current_data["broken_code"])
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(current_data["test_code"])
                
            initial_state = {
                "incident_report": incident_text,
                "target_file": target_file,
                "code_content": current_data["broken_code"],
                "test_file": test_file,
                "test_output": "",
                "attempt_count": 0,
                "status": "pending",
                "logs": [],
                "gemini_api_key": gemini_key
            }
            
            app_graph = build_agent_graph()
            with st.spinner("Agent diagnosing and executing sandbox tools..."):
                try:
                    final_state = app_graph.invoke(initial_state)
                    st.session_state["final_state"] = final_state
                except Exception as ex:
                    st.error(f"Agent Execution Failed: {str(ex)}")

with col_right:
    st.subheader("2. Real-Time Autonomous Execution Trail")
    if "final_state" in st.session_state:
        state = st.session_state["final_state"]
        for log_entry in state.get("logs", []):
            st.markdown(f"`{log_entry}`")
            
        st.divider()
        st.subheader("3. Resulting Sandbox Patch")
        if os.path.exists(state["target_file"]):
            with open(state["target_file"], "r", encoding="utf-8") as f:
                fixed_code = f.read()
            st.code(fixed_code, language="python")
            
        if state["status"] == "passed":
            st.success("🎯 Incident autonomously remediated and verified in sandbox!")
        else:
            st.error("⚠️ Escalated to human SRE.")
    else:
        st.info("Select a scenario, enter your key, and trigger the outage.")