import streamlit as st
import os
from agent import build_agent_graph

st.set_page_config(page_title="DevSentry AI", page_icon="🛡️", layout="wide")

st.title("🛡️ DevSentry: Autonomous Self-Healing SRE")
st.caption("AIC Competition 2026-2027 | Goal ➔ Decide ➔ Tool ➔ Observe ➔ Finish")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Incident Alert Payload")
    incident_text = st.text_area(
        "Simulated Alert Payload",
        value="CRITICAL ALERT: HTTP 500 in Checkout Engine. ZeroDivisionError when applying a 0-item coupon.",
        height=90
    )
    
    target_file = st.text_input("Vulnerable File Path", value="discount_service.py")
    test_file = st.text_input("Test Suite Path", value="test_discount.py")
    
    if st.button("🔥 Simulate Outage & Launch Agent", type="primary"):
        mock_broken_code = (
            "def calculate_discount(total_amount, items_count):\n"
            "    # Bug: Division by zero when items_count == 0\n"
            "    discount_ratio = 10 / items_count\n"
            "    return total_amount - (total_amount * discount_ratio)\n"
        )
        mock_test_code = (
            "from discount_service import calculate_discount\n"
            "assert calculate_discount(100, 2) == 100 - (100 * 5)\n"
            "assert calculate_discount(50, 0) == 50\n"
            "print('ALL_TESTS_PASSED')\n"
        )
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(mock_broken_code)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(mock_test_code)
            
        initial_state = {
            "incident_report": incident_text,
            "target_file": target_file,
            "code_content": mock_broken_code,
            "test_file": test_file,
            "test_output": "",
            "attempt_count": 0,
            "status": "pending",
            "logs": []
        }
        
        app_graph = build_agent_graph()
        with st.spinner("Agent running iterative diagnosis and patch loop..."):
            final_state = app_graph.invoke(initial_state)
            st.session_state["final_state"] = final_state

with col_right:
    st.subheader("2. Real-Time Autonomous Execution Trail")
    if "final_state" in st.session_state:
        state = st.session_state["final_state"]
        for log_entry in state.get("logs", []):
            st.markdown(f"`{log_entry}`")
            
        st.divider()
        st.subheader("3. Resulting Sandbox Patch")
        with open(state["target_file"], "r", encoding="utf-8") as f:
            fixed_code = f.read()
        st.code(fixed_code, language="python")
        
        if state["status"] == "passed":
            st.success("🎯 Incident autonomously remediated and verified in sandbox!")
        else:
            st.error("⚠️ Escalated to human SRE.")
    else:
        st.info("Trigger an outage from the left panel to watch the agent loop live.")