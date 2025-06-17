from typing import Dict, Optional
from dotenv import load_dotenv

from app.utils.llm import LLMInitializer
from .states import WorkflowState, CampaignState
from .workflow import WorkflowBuilder
from .agent_handlers import AgentHandlers
from .response_formatter import ResponseFormatter

class OrchestratorAgent:
    def __init__(self):
        load_dotenv()
        self.llm = LLMInitializer().llm
        self.agent_handlers = AgentHandlers(self.llm)
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        agent_methods = {
            "analyze_user_input": self.agent_handlers.analyze_user_input,
            "gather_data": self.agent_handlers.gather_data,
            "analyze_data": self.agent_handlers.analyze_data,
            "generate_recommendations": self.agent_handlers.generate_recommendations,
            "generate_summary": self.agent_handlers.generate_summary,
            "route_after_analysis": self.agent_handlers.route_after_analysis
        }
        return WorkflowBuilder.create_workflow(agent_methods)

    def run(self,
            user_input: str,
            feedback: Optional[str] = None,
            context: Optional[Dict] = None) -> Dict:
        """Run the workflow with user input and context"""
        try:
            initial_state = WorkflowState(
                current_state=CampaignState.DATA_GATHERING,
                user_input=user_input,
                feedback=feedback,
                context=context or {}
            )

            compiled_workflow = self.workflow.compile()
            final_state = compiled_workflow.invoke(initial_state)

            # Convert final_state to dict if it isn't already
            if not isinstance(final_state, dict):
                final_state = final_state.dict()

            return ResponseFormatter.format_success_response(final_state, context)

        except Exception as e:
            return ResponseFormatter.format_error_response(e)