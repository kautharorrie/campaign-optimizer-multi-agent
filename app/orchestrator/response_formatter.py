from datetime import datetime
from typing import Dict, Any
from app.agents.user_input_analysis_agent import UserInputType

class ResponseFormatter:
    @staticmethod
    def format_success_response(final_state: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """Format successful response from workflow execution"""
        if final_state.get('user_input_type') == UserInputType.DONE:
            return {
                "message": "Conversation ended. Goodbye!",
                "status": "ended",
                "user_input_type": UserInputType.DONE.value
            }

        return {
            "user_input_type": (final_state.get('user_input_type') or UserInputType.RECOMMENDATION).value,
            "campaign_data": final_state.get('campaign_data', {}),
            "analysis": final_state.get('analysis_results', {}),
            "recommendations": final_state.get('recommendations', []),
            "summary": final_state.get('summary', {}),
            "context": {
                "had_previous_interaction": bool(context and context.get('conversation_history')),
                "conversation_history": context.get('conversation_history', []) if context else [],
                "timestamp": datetime.now().isoformat()
            }
        }

    @staticmethod
    def format_error_response(error: Exception) -> Dict[str, Any]:
        """Format error response"""
        return {
            "error": str(error),
            "user_input_type": UserInputType.RECOMMENDATION.value,
            "recommendations": ["An error occurred while processing your request."],
            "context": {
                "error_timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__
            }
        }