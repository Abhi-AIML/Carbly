import html
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from services.gemini_service import get_chat_response

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    history: List[ChatMessage]
    phase: str = "onboarding"

class ChatResponse(BaseModel):
    reply: str
    data_collected: bool
    carbly_data: Optional[Dict[str, Any]] = None

def sanitize_input(text: str) -> str:
    # Basic sanitization
    return html.escape(text.strip())

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    sanitized_message = sanitize_input(request.message)
    
    # Sanitize history
    sanitized_history = []
    for msg in request.history:
        sanitized_history.append({
            "role": msg.role,
            "content": sanitize_input(msg.content)
        })
        
    reply, data_collected, carbly_data = get_chat_response(
        history=sanitized_history,
        user_message=sanitized_message,
        phase=request.phase
    )
    
    return ChatResponse(
        reply=reply,
        data_collected=data_collected,
        carbly_data=carbly_data
    )
