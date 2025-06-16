from typing import Dict
from uuid import uuid4
from agents.orchestrator_v2 import OrchestratorAgent
from utils.conversation_manager import ConversationManager, MessageType

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

            # Process message
            result = self.orchestrator.run(
                user_input=user_message,
                context=context
            )

            # Handle response based on type
            if result.get('user_input_type') == 'SUMMARY':
                response_content = result.get('summary', {}).get('content',
                                                                 "Unable to generate summary. Please try again.")
            elif result.get('recommendations'):
                response_content = "\n\n".join(result['recommendations'])
            else:
                response_content = "Unable to process request. Please try again."

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
                'session_id': session_id
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
                'session_id': session_id
            }

    def get_session_history(self, session_id: str):
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
