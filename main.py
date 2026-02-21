from agent import create_zionx_agent
from memory import load_facts, save_fact

_agent = None


def get_agent():
    """Return the singleton ZionX agent, creating it on first call."""
    global _agent
    if _agent is None:
        _agent = create_zionx_agent()
    return _agent


def run(message: str, thread_id: str = "default") -> str:
    """Send a message to the orchestrator and return its response.

    Args:
        message: The user's input (already converted to text).
        thread_id: Conversation thread identifier for short-term memory isolation.
    """
    config = {"configurable": {"thread_id": thread_id}}

    messages: list = [{"role": "user", "content": message}]
    facts = load_facts(thread_id)
    if facts:
        messages.insert(0, {"role": "system", "content": f"[Known facts about this user]\n{facts}"})

    result = get_agent().invoke({"messages": messages}, config=config)

    structured: "Chat" = result["structured_response"]
    if structured.fact:
        save_fact(thread_id, structured.fact)

    return structured.normal_response


# ── Quick CLI test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(run("I'm 7 months pregnant and I've been having headaches. What should I do?"))
