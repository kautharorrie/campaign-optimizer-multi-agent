from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.orchestrator.orchestrator import OrchestratorAgent
from app.utils.conversation_manager import ConversationManager, MessageType
from typing import Optional

app = FastAPI()
orchestrator = OrchestratorAgent()
conversation_manager = ConversationManager()

class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    if not session_id:
        # Create new session if none provided
        session_id = conversation_manager.create_session(session_id).session_id
    elif session_id not in conversation_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Record user message
    conversation_manager.add_message(
        session_id=session_id,
        content=request.user_input,
        msg_type=MessageType.USER_INPUT
    )

    # Get conversation context
    context = {
        'conversation_history': conversation_manager.get_conversation_history(session_id),
        'session_id': session_id
    }

    # Run the LangGraph workflow with user input and context
    result = orchestrator.run(request.user_input, context=context)

    # Record system response
    response_content = f"Analysis: {result['analysis']}\nRecommendations: {', '.join(result['recommendations'])}"
    conversation_manager.add_message(
        session_id=session_id,
        content=response_content,
        msg_type=MessageType.SYSTEM_RESPONSE,
        metadata={
            'campaign_data': result['campaign_data'],
            'analysis': result['analysis'],
            'recommendations': result['recommendations']
        }
    )

    return {
        "session_id": session_id,
        "campaign_data": result["campaign_data"],
        "analysis": result["analysis"],
        "recommendations": result["recommendations"],
        "conversation_history": conversation_manager.get_conversation_history(session_id)
    }

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    if session_id not in conversation_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "history": conversation_manager.get_conversation_history(session_id)
    }