from agent import create_zionx_agent

agent = create_zionx_agent()


def run(message: str, thread_id: str = "default") -> str:
    """Send a message to the orchestrator and return its response.

    Args:
        message: The user's input (already converted to text).
        thread_id: Conversation thread identifier for short-term memory isolation.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )
    return result["messages"][-1].content


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(run("I'm 7 months pregnant and I've been having headaches. What should I do?"))
