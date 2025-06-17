from typing import Dict, Tuple, Optional
from uuid import uuid4
from app.orchestrator.orchestrator import OrchestratorAgent
from app.utils.conversation_manager import ConversationManager, MessageType
from app.agents.user_input_analysis_agent import UserInputType

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
        """
        Process a user message and return appropriate response
        Returns:
            Dict containing response data including:
            - type: str
            - content: str
            - session_id: str
            - is_done: bool
        """
        try:
            # Record user message
            self.conversation_manager.add_message(
                session_id=session_id,
                content=user_message,
                msg_type=MessageType.USER_INPUT
            )

            # Get conversation context
            context = {
                'conversation_history': self.conversation_manager.get_conversation_history(session_id),
                'session_id': session_id
            }

            # Process message through orchestrator
            result = self.orchestrator.run(
                user_input=user_message,
                context=context
            )

            # Check if we're in DONE state
            is_done = result.get('user_input_type') == 'DONE'

            # Handle response based on type
            response_content = self._format_response_content(result)

            # Record system response
            self.conversation_manager.add_message(
                session_id=session_id,
                content=response_content,
                msg_type=MessageType.SYSTEM_RESPONSE,
                metadata={
                    'user_input_type': result.get('user_input_type'),
                    'context': result.get('context', {})
                }
            )

            return {
                'type': 'response',
                'content': response_content,
                'session_id': session_id,
                'user_input_type': result.get('user_input_type'),
                'is_done': is_done
            }

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(f"❌ Error in process_message: {str(e)}")

            self.conversation_manager.add_message(
                session_id=session_id,
                content=error_message,
                msg_type=MessageType.SYSTEM_RESPONSE,
                metadata={'error': True}
            )

            return {
                'type': 'error',
                'content': error_message,
                'session_id': session_id,
                'is_done': False
            }

    def _format_response_content(self, result: Dict) -> str:
        """Format the response content based on result type"""
        if result.get('user_input_type') == 'DONE':
            return "Thank you for using the service. Goodbye!"

        if result.get('user_input_type') == 'SUMMARY':
            return result.get('summary', {}).get('content',
                                                 "Unable to generate summary. Please try again.")

        if result.get('recommendations'):
            return "\n\n".join(result['recommendations'])

        return "Unable to process request. Please try again."

    def get_session_history(self, session_id: str) -> list:
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
