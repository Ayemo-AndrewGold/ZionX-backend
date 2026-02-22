"""Quick test to verify all changes work correctly"""

from agent import Chat, create_zionx_agent
from tools import ALL_TOOLS

print("=" * 60)
print("ZionX System Check")
print("=" * 60)

# Test 1: Chat model fields
print("\n1. Chat Model Fields:")
print(f"   Fields: {list(Chat.model_fields.keys())}")
assert "normal_response" in Chat.model_fields
assert "fact" in Chat.model_fields
assert "risk_level" in Chat.model_fields
assert "urgency" in Chat.model_fields
print("   ✓ All fields present")

# Test 2: Tools loaded
print("\n2. Specialist Tools:")
tool_names = [t.name for t in ALL_TOOLS]
print(f"   Total: {len(ALL_TOOLS)} tools")
for name in tool_names:
    print(f"   - {name}")

expected_tools = [
    'emergency_triage',
    'pregnancy_advisor',
    'diabetes_advisor',
    'pediatrics_advisor',
    'mental_health_advisor',
    'preventive_health_analyzer'
]
for tool in expected_tools:
    assert tool in tool_names, f"Missing tool: {tool}"
print("   ✓ All tools loaded")

# Test 3: Agent creation
print("\n3. Agent Creation:")
try:
    agent = create_zionx_agent()
    print("   ✓ Agent created successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    raise

print("\n" + "=" * 60)
print("All checks passed! ✓")
print("=" * 60)
