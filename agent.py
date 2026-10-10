import subprocess
from typing import TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    incident_report: str
    target_file: str
    code_content: str
    test_file: str
    test_output: str
    attempt_count: int
    status: str
    logs: List[str]

def run_sandbox_eval(test_path: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["python", test_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return proc.returncode, proc.stdout + "\n" + proc.stderr
    except Exception as e:
        return 1, str(e)

def diagnose_issue(state: AgentState) -> dict:
    new_logs = list(state.get("logs", []))
    new_logs.append("🔍 Diagnostic Node: Executing test reproduction script...")
    
    code, output = run_sandbox_eval(state["test_file"])
    if code != 0:
        new_logs.append(f"❌ Reproduction confirmed! Sandbox returned exit code {code}.")
        new_status = "failing"
    else:
        new_logs.append("✅ Tests passed initially.")
        new_status = "passed"
        
    return {
        "test_output": output,
        "status": new_status,
        "logs": new_logs,
        "attempt_count": state.get("attempt_count", 0)
    }

def generate_patch(state: AgentState) -> dict:
    new_logs = list(state.get("logs", []))
    attempt = state["attempt_count"] + 1
    new_logs.append(f"🛠️ Patch Engine: Running self-correction attempt #{attempt}...")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    prompt = f"""
    Incident Report: {state['incident_report']}
    
    Current File Content:
    {state['code_content']}
    
    Runtime Failure / Traceback:
    {state['test_output']}
    
    Fix the bug. Output ONLY the raw replacement python code for the target file.
    Do not wrap inside markdown ticks (```python). Return only executable code.
    """
    
    res = llm.invoke([
        SystemMessage(content="You are an autonomous SRE patch agent. Return raw code only."),
        HumanMessage(prompt)
    ])
    
    clean_code = res.content.replace("```python", "").replace("```", "").strip()
    
    with open(state["target_file"], "w", encoding="utf-8") as f:
        f.write(clean_code)
        
    new_logs.append(f"💾 Applied patch to '{state['target_file']}'. Validating in sandbox...")
    
    code, output = run_sandbox_eval(state["test_file"])
    if code == 0:
        new_logs.append(f"✅ Sandbox validation successful on attempt #{attempt}!")
        new_status = "passed"
    else:
        last_line = output.strip().splitlines()[-1] if output.strip() else "Unknown error"
        new_logs.append(f"⚠️ Patch failed assertions. Stderr: {last_line}")
        new_status = "failing"
        
    return {
        "code_content": clean_code,
        "test_output": output,
        "status": new_status,
        "attempt_count": attempt,
        "logs": new_logs
    }

def package_pr(state: AgentState) -> dict:
    new_logs = list(state.get("logs", []))
    new_logs.append("🚀 Deployment Node: Generating pull request and audit trail...")
    new_logs.append(f"📦 PR Title: fix(auto): resolve incident via validated patch in {state['target_file']}")
    new_logs.append("✨ All unit tests green. Ready for production merge.")
    return {"logs": new_logs}

def router(state: AgentState) -> str:
    if state["status"] == "passed":
        return "deploy"
    if state["attempt_count"] >= 3:
        return "escalate"
    return "retry"

def build_agent_graph():
    builder = StateGraph(AgentState)
    builder.add_node("diagnose", diagnose_issue)
    builder.add_node("patcher", generate_patch)
    builder.add_node("deploy", package_pr)
    
    builder.set_entry_point("diagnose")
    builder.add_conditional_edges(
        "diagnose",
        lambda s: "deploy" if s["status"] == "passed" else "patcher",
        {"deploy": "deploy", "patcher": "patcher"}
    )
    builder.add_conditional_edges(
        "patcher",
        router,
        {"deploy": "deploy", "retry": "patcher", "escalate": END}
    )
    builder.add_edge("deploy", END)
    return builder.compile()