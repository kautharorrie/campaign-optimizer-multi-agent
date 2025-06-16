from typing import Dict, Optional, List
from uuid import uuid4
from datetime import datetime
from agents.orchestrator_v2 import OrchestratorAgent
from utils.conversation_manager import ConversationManager, MessageType
from agents.user_input_analysis_agent import UserInputType

class InteractiveSession:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.conversation_manager = ConversationManager()

    def start_session(self) -> str:
        """Start a new conversation session"""
        session_id = str(uuid4())
        self.conversation_manager.create_session(session_id)
        return session_id

    def process_message(self, session_id: str, user_message: str) -> Dict:
        """Process a user message and return appropriate response"""
        # Record user message
        self.conversation_manager.add_message(
            session_id=session_id,
            content=user_message,
            msg_type=MessageType.USER_INPUT
        )

        # Get conversation context
        context = self.conversation_manager.get_context(session_id)
        recent_messages = self.conversation_manager.get_conversation_history(
            session_id=session_id,
            limit=5
        )

        # Check if this is feedback to previous response
        last_system_message = next(
            (msg for msg in reversed(recent_messages)
             if msg.type == MessageType.SYSTEM_RESPONSE),
            None
        )

        if last_system_message:
            # Process as potential feedback
            result = self.orchestrator.run(
                user_input=user_message,
                feedback=user_message if self._is_feedback(user_message) else None,
                context=context
            )

            if result.get('feedback_analysis'):
                # This was processed as feedback
                self.conversation_manager.add_message(
                    session_id=session_id,
                    content=user_message,
                    msg_type=MessageType.USER_FEEDBACK,
                    metadata=result['feedback_analysis']
                )

                # Add refined response
                if result.get('summary', {}).get('refined_summary'):
                    self.conversation_manager.add_message(
                        session_id=session_id,
                        content=result['summary']['refined_summary'],
                        msg_type=MessageType.SYSTEM_REFINEMENT
                    )
                    return {
                        'type': 'refinement',
                        'content': result['summary']['refined_summary'],
                        'session_id': session_id
                    }

        # Process as new request
        result = self.orchestrator.run(
            user_input=user_message,
            context=context
        )

        # Record system response
        response_content = result.get('summary', {}).get('summary', '')
        self.conversation_manager.add_message(
            session_id=session_id,
            content=response_content,
            msg_type=MessageType.SYSTEM_RESPONSE,
            metadata={'user_input_type': result['user_input_type']}
        )

        return {
            'type': 'response',
            'content': response_content,
            'session_id': session_id
        }

    def _is_feedback(self, message: str) -> bool:
        """
        Determine if a message is likely feedback
        This could be enhanced with more sophisticated analysis
        """
        feedback_indicators = [
            "could you", "please make", "instead", "rather",
            "better if", "prefer", "good but", "nice but",
            "improve", "change", "update", "modify"
        ]
        return any(indicator in message.lower() for indicator in feedback_indicators)

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get formatted conversation history"""
        messages = self.conversation_manager.get_conversation_history(session_id)
        return [
            {
                'content': msg.content,
                'type': msg.type.value,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata
            }
            for msg in messages
        ]
