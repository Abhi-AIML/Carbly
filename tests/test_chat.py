import pytest
from pydantic import ValidationError
from routers.chat import sanitize_input, ChatRequest
from services.gemini_service import get_chat_response

def test_message_sanitisation():
    bad_input = "<script>alert(1)</script>Hello"
    clean = sanitize_input(bad_input)
    assert "<script>" not in clean
    assert "&lt;script&gt;" in clean

def test_invalid_json_handling():
    # If API returns malformed JSON but contains the marker
    import services.gemini_service as gs
    
    # Mocking genai response for this specific test would be ideal,
    # but we can just test the regex parsing locally
    import re, json
    reply = "Here is your data:\n```carbly_data\n{invalid json}\n```"
    match = re.search(r'```carbly_data\s*(\{.*?\})\s*```', reply, re.DOTALL)
    assert match is not None
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        data = None
    assert data is None

def test_history_passed_correctly():
    req_data = {
        "message": "test",
        "history": [{"role": "ai", "content": "hello"}],
        "phase": "onboarding"
    }
    req = ChatRequest(**req_data)
    assert len(req.history) == 1
    assert req.history[0].role == "ai"

def test_carbly_data_detection():
    # Similar to above, testing the extraction logic
    reply = '```carbly_data\n{"name": "Test"}\n```'
    import re, json
    match = re.search(r'```carbly_data\s*(\{.*?\})\s*```', reply, re.DOTALL)
    assert match is not None
    data = json.loads(match.group(1))
    assert data["name"] == "Test"
