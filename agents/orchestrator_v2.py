from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from datetime import datetime

from agents.analysis_agent import AnalysisAgent
from agents.data_gathering_agent import DataGatheringAgent
from agents.recommendation_agent import RecommendationAgent
from agents.summary_agent import SummaryAgent
from agents.user_input_analysis_agent import UserInputAnalysisAgent, UserInputType
from utils.llm import LLMInitializer

class CampaignState(Enum):
    DATA_GATHERING = "DATA_GATHERING"
    ANALYSIS = "ANALYSIS"
    RECOMMENDATION_GENERATION = "RECOMMENDATION_GENERATION"
    SUMMARY_GENERATION = "SUMMARY_GENERATION"

class WorkflowState(BaseModel):
    current_state: CampaignState
    campaign_data: Optional[Dict] = None
    analysis_results: Optional[Dict] = None
    recommendations: Optional[List[str]] = None
    summary: Optional[Dict] = None
    user_input: Optional[str] = None
    user_input_type: Optional[UserInputType] = None
    feedback: Optional[str] = None
    context: Optional[Dict] = None
    recommendation_context: Optional[Dict] = None
    summary_context: Optional[Dict] = None

class OrchestratorAgent:
    def __init__(self):
        load_dotenv()
        self.llm = LLMInitializer().llm
        self.user_input_agent = UserInputAnalysisAgent(self.llm)
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze_user_input", self._analyze_user_input)
        workflow.add_node("gather_data", self._gather_data)
        workflow.add_node("analyze_data", self._analyze_data)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("generate_summary", self._generate_summary)

        # Add conditional edge after input analysis
        workflow.add_conditional_edges(
            "analyze_user_input",
            lambda state: "end" if state.user_input_type == UserInputType.DONE else "gather_data",
            {
                "gather_data": "gather_data",
                "end": END
            }
        )

        # Rest of the workflow remains the same
        workflow.add_edge("gather_data", "analyze_data")
        workflow.add_conditional_edges(
            "analyze_data",
            self._route_after_analysis,
            {
                "generate_summary": "generate_summary",
                "generate_recommendations": "generate_recommendations",
                "end": END
            }
        )

        workflow.add_edge("generate_recommendations", END)
        workflow.add_edge("generate_summary", END)

        workflow.set_entry_point("analyze_user_input")
        return workflow

    def _analyze_user_input(self, state: WorkflowState) -> WorkflowState:
        """Analyze user input to determine intent"""
        analysis_result = self.user_input_agent.analyze_input(state.user_input)
        state.user_input_type = analysis_result["type"]
        print(f"📝 User input classified as: {state.user_input_type.value}")
        return state

    def _gather_data(self, state: WorkflowState) -> WorkflowState:
        """Gather campaign data"""
        data_agent = DataGatheringAgent()
        campaign_id = "CAMPAIGN123"
        print(f"🔍 Gathering context for campaign: fintech summer promo")
        campaign_data = data_agent.gather_campaign_context(campaign_id)
        print(f"\n📊 Campaign data gathered: {campaign_data}")
        state.campaign_data = campaign_data
        state.current_state = CampaignState.DATA_GATHERING
        return state

    def _analyze_data(self, state: WorkflowState) -> WorkflowState:
        """Analyze campaign data"""
        analysis_agent = AnalysisAgent(llm=self.llm)
        print("📊 Analyzing campaign data with AnalysisAgent...")

        if not state.campaign_data:
            raise ValueError("No campaign data to analyze.")

        analysis_result = analysis_agent.analyze_campaign(state.campaign_data)
        state.analysis_results = analysis_result
        state.current_state = CampaignState.ANALYSIS
        print("📈 Analysis complete.")
        return state

    def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        """Generate recommendations"""
        try:
            recommendation_agent = RecommendationAgent(llm=self.llm)
            print("🔍 Generating recommendations...")

            # Validate required data
            if not state.campaign_data:
                raise ValueError("Campaign data is missing")
            if not state.analysis_results:
                raise ValueError("Analysis results are missing")

            # Generate recommendations
            rec_result = recommendation_agent.generate_recommendations(
                campaign_data=state.campaign_data,
                analysis=state.analysis_results,
                conversation_history=state.context.get('conversation_history', [])
            )

            # Ensure rec_result is not None
            if not rec_result:
                raise ValueError("Recommendation generation returned None")

            # Extract recommendations with fallback
            recommendations = rec_result.get("recommendations", [])
            if not recommendations:
                recommendations = ["No specific recommendations available at this time."]

            # Update state
            state.recommendations = recommendations
            state.recommendation_context = {
                "timestamp": datetime.now().isoformat(),
                "template_used": rec_result.get("template_used", False),
                "had_previous_interaction": bool(state.context.get('conversation_history'))
            }

            print("✅ Recommendations generated successfully")
            return state

        except Exception as e:
            print(f"❌ Error in recommendation generation: {str(e)}")
            state.recommendations = [f"Unable to generate recommendations: {str(e)}"]
            state.recommendation_context = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            return state

    def _generate_summary(self, state: WorkflowState) -> WorkflowState:
        """Generate summary using SummaryAgent"""
        try:
            summary_agent = SummaryAgent(llm=self.llm)
            print("📊 Generating summary...")

            summary_result = summary_agent.generate_summary(
                campaign_data=state.campaign_data,
                analysis_results=state.analysis_results,
                conversation_history=state.context.get('conversation_history', [])
            )

            state.summary = summary_result
            print("✅ Summary generated successfully")
            return state

        except Exception as e:
            print(f"❌ Error in summary generation: {str(e)}")
            state.summary = {
                "content": "Unable to generate summary at this time.",
                "error": str(e)
            }
        return state

    def _route_after_analysis(self, state: WorkflowState) -> str:
        """Route to appropriate next step based on user input type"""
        if state.user_input_type == UserInputType.SUMMARY:
            return "generate_summary"
        elif state.user_input_type == UserInputType.RECOMMENDATION:
            return "generate_recommendations"
        elif state.user_input_type == UserInputType.DONE:
            return "end"
        return "generate_recommendations"  # default path
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
            # If user wants to end the conversation
            if final_state.user_input_type == UserInputType.DONE:
                return {
                    "message": "Conversation ended. Goodbye!",
                    "status": "ended",
                    "user_input_type": UserInputType.DONE.value
            }

            # Convert final_state to dict if it isn't already
            if not isinstance(final_state, dict):
                final_state = final_state.dict()

            response = {
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

            return response

        except Exception as e:
            print(f"❌ Error in workflow execution: {str(e)}")
            return {
                "error": str(e),
                "user_input_type": UserInputType.RECOMMENDATION.value,
                "recommendations": ["An error occurred while processing your request."],
                "context": {
                    "error_timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
            }




if __name__ == "__main__":
    orchestrator = OrchestratorAgent()

    # Test summary generation
    summary_result = orchestrator.run("Can you summarize the campaign performance?")
    print("\n📊 Summary Request Results:")
    if summary_result.get('summary'):
        print(f"Campaign: {summary_result['summary'].get('campaign_name')}")
        print(f"Summary: {summary_result['summary'].get('summary')}")
        print(f"Key Metrics: {summary_result['summary'].get('key_metrics')}")

    # Test recommendation generation
    rec_result = orchestrator.run("What improvements would you recommend?")
    print("\n💡 Recommendation Request Results:")
    print(f"Recommendations: {rec_result.get('recommendations')}")

