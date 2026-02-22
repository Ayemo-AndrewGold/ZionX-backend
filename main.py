from agent import create_zionx_agent
from core.models import Chat
from memory import load_facts, save_fact
from users import get_user_profile_context
from daily_tracking import get_tracking_summary
from emergency_alerts import send_emergency_alert, should_trigger_emergency_alert

_agent = None


def get_agent():
    """Return the singleton ZionX agent, creating it on first call."""
    global _agent
    if _agent is None:
        _agent = create_zionx_agent()
    return _agent


def run(message: str, thread_id: str = "default", user_id: str = "guest") -> dict:
    """Send a message to the orchestrator and return its response.

    Args:
        message: The user's input (already converted to text).
        thread_id: Conversation thread identifier for short-term memory isolation.
        user_id: User identifier for long-term memory isolation.
        
    Returns:
        dict with keys: response, risk_level, urgency, emergency_alert_sent
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}

        messages: list = [{"role": "user", "content": message}]
        
        # Build comprehensive context from multiple sources
        context_parts = []
        
        # 1. Long-term memory (facts from past interactions)
        facts = load_facts(user_id)
        if facts:
            context_parts.append(f"[Long-term memory - Past interactions]\n{facts}")
        
        # 2. Onboarding profile data (medical info, allergies, etc.)
        profile_context = get_user_profile_context(user_id)
        if profile_context:
            context_parts.append(f"[User Profile - From Onboarding]\n{profile_context}")
        
        # 3. Recent tracking data (daily health updates)
        tracking_summary = get_tracking_summary(user_id, days=7)
        if tracking_summary:
            context_parts.append(f"[Recent Health Tracking]\n{tracking_summary}")
        
        # Combine all context
        if context_parts:
            full_context = "\n\n".join(context_parts)
            messages.insert(0, {"role": "system", "content": full_context})

        result = get_agent().invoke({"messages": messages}, config=config)

        structured: Chat = result["structured_response"]
        
        # Save new facts to long-term memory
        if structured.fact:
            save_fact(user_id, structured.fact)
        
        # Check if emergency alert should be triggered
        emergency_alert_sent = False
        if should_trigger_emergency_alert(structured.risk_level, structured.urgency):
            # Attempt to send emergency alert
            success, alert_message = send_emergency_alert(user_id, {
                "severity": structured.risk_level,
                "symptoms": message,
                "ai_assessment": structured.normal_response,
                "user_location": "Not provided"  # Could be enhanced with location tracking
            })
            emergency_alert_sent = success
            
            if success:
                # Append alert confirmation to response
                structured.normal_response += f"\n\n **Emergency Alert Sent**: {alert_message}"

        return {
            "response": structured.normal_response,
            "risk_level": structured.risk_level,
            "urgency": structured.urgency,
            "emergency_alert_sent": emergency_alert_sent
        }
    except Exception as e:
        print(f"Error in run(): {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": f"I encountered an error processing your request. Please try rephrasing or contact support if this persists.",
            "risk_level": None,
            "urgency": None,
            "emergency_alert_sent": False
        }


# if __name__ == "__main__":
#     print(run("I'm 7 months pregnant and I've been having headaches. What should I do?"))
