"""
SOVEREIGN-Ω · LangChain Integration
=====================================
Wraps SOVEREIGN-Ω's 4 free skills as native LangChain tools.
Drop these tools into any AgentExecutor or LangGraph workflow.

Requirements: pip install requests langchain langchain-openai
"""

import json
import requests
from typing import Optional
from langchain.tools import Tool

BASE = "https://sovereignomega.onrender.com"
INVOKE = f"{BASE}/api/v1/skills/invoke"


def _post(skill_id: str, data: dict) -> str:
    try:
        r = requests.post(f"{INVOKE}/{skill_id}", json={"skill_id": skill_id, "input": data}, timeout=15)
        return json.dumps(r.json().get("output", r.json()), indent=2)
    except Exception as e:
        return f"Error calling {skill_id}: {e}"


# ─── Tool 1: Coherence Evaluator ─────────────────────────────────────────────
def coherence_evaluate(query: str) -> str:
    """Evaluate cognitive coherence of a proposed action using TRION math (5 planes).
    Returns Ψ score, gate decision (ACT/SILENCE), and per-plane breakdown."""
    return _post("coherence_evaluate", {"query": query, "domain": "general"})

coherence_tool = Tool(
    name="sovereign_coherence_evaluate",
    func=coherence_evaluate,
    description=(
        "Use this before any important action. Evaluates cognitive coherence across 5 planes "
        "(Perceptual, Inferential, Consensus, Self-Reflection, World Model). "
        "Returns psi_score (0–1), gate_open (bool), and plane_breakdown. "
        "Input: the proposed action or question as a plain string."
    )
)


# ─── Tool 2: Silence Check ────────────────────────────────────────────────────
def silence_check(action: str) -> str:
    """Check if a specific action should be silenced by the Silence Protocol."""
    return _post("silence_check", {"proposed_action": action, "stakes": 0.7})

silence_tool = Tool(
    name="sovereign_silence_check",
    func=silence_check,
    description=(
        "Use before high-stakes actions. Returns silenced (bool) + reason. "
        "If silenced=true, do NOT proceed with the action. "
        "Input: description of the action you're about to take."
    )
)


# ─── Tool 3: Moat Status ──────────────────────────────────────────────────────
def moat_status(_: str = "") -> str:
    """Query the compounding intelligence moat Λ. Λ never decreases."""
    return _post("moat_status", {})

moat_tool = Tool(
    name="sovereign_moat_status",
    func=moat_status,
    description=(
        "Returns the current Λ (compounding intelligence moat), IQ score, cycle count, "
        "and domain mastery. Use to assess agent reputation and intelligence growth. "
        "No input required."
    )
)


# ─── Tool 4: Intelligence Score ───────────────────────────────────────────────
def intelligence_score(_: str = "") -> str:
    """Get the full IQ breakdown with domain mastery and 30-day projection."""
    return _post("intelligence_score", {"include_projection": True})

intelligence_tool = Tool(
    name="sovereign_intelligence_score",
    func=intelligence_score,
    description=(
        "Returns full IQ breakdown: score, lambda, cycles, domain mastery, "
        "30/90/365-day projections. Use to evaluate agent's accumulated knowledge. "
        "No input required."
    )
)


# ─── Assemble Tools ───────────────────────────────────────────────────────────
SOVEREIGN_TOOLS = [
    coherence_tool,
    silence_tool,
    moat_tool,
    intelligence_tool,
]


# ─── Example: Wire into a LangChain agent ────────────────────────────────────
if __name__ == "__main__":
    print("SOVEREIGN-Ω LangChain Tools loaded:")
    for t in SOVEREIGN_TOOLS:
        print(f"  - {t.name}")

    print("\nTesting coherence_evaluate directly:")
    result = coherence_evaluate("Should I execute a market buy order for ETH?")
    print(result)

    print("\nTo use in LangChain AgentExecutor:")
    print("""
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o")
    agent = create_openai_tools_agent(llm, SOVEREIGN_TOOLS, prompt)
    executor = AgentExecutor(agent=agent, tools=SOVEREIGN_TOOLS)
    executor.invoke({"input": "Check if market conditions are coherent for a BTC trade"})
    """)

    print("\nMCP config for any MCP host:")
    print(json.dumps({
        "mcpServers": {
            "sovereign-omega": {
                "url": f"{BASE}/api/v1/mcp",
                "transport": "http"
            }
        }
    }, indent=2))
