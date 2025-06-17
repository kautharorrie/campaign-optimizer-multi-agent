from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class MessageType(Enum):
    USER_INPUT = "USER_INPUT"
    SYSTEM_RESPONSE = "SYSTEM_RESPONSE"
    USER_FEEDBACK = "USER_FEEDBACK"
    SYSTEM_REFINEMENT = "SYSTEM_REFINEMENT"

class Message(BaseModel):
    content: str
    type: MessageType
    timestamp: datetime = datetime.now()
    metadata: Dict = {}

class ConversationSession(BaseModel):
    session_id: str
    start_time: datetime = datetime.now()
    messages: List[Message] = []
    context: Dict = {}
    active: bool = True

class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}

    def create_session(self, session_id: str) -> ConversationSession:
        """Create a new conversation session"""
        session = ConversationSession(session_id=session_id)
        self.sessions[session_id] = session
        return session

    def add_message(self,
                   session_id: str,
                   content: str,
                   msg_type: MessageType,
                    metadata=None) -> Message:
        """Add a message to the conversation history"""
        if metadata is None:
            metadata = {}
        if session_id not in self.sessions:
            self.create_session(session_id)

        message = Message(
            content=content,
            type=msg_type,
            metadata=metadata
        )

        self.sessions[session_id].messages.append(message)
        return message

    def get_conversation_history(self,
                               session_id: str,
                               limit: int = None) -> List[Message]:
        """Get conversation history for a session"""
        if session_id not in self.sessions:
            return []

        messages = self.sessions[session_id].messages
        if limit:
            return messages[-limit:]
        return messages

    def get_context(self, session_id: str) -> Dict:
        """Get conversation context"""
        if session_id not in self.sessions:
            return {}
        return self.sessions[session_id].context

    def update_context(self, session_id: str, new_context: Dict):
        """Update conversation context"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        self.sessions[session_id].context.update(new_context)
