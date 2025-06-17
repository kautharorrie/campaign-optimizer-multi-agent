from datetime import datetime
from typing import Dict
from app.agents.analysis_agent import AnalysisAgent
from app.agents.data_gathering_agent import DataGatheringAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.user_input_analysis_agent import UserInputAnalysisAgent, UserInputType
from .states import WorkflowState

class AgentHandlers:
    def __init__(self, llm):
        self.llm = llm
        self.user_input_agent = UserInputAnalysisAgent(self.llm)

    def analyze_user_input(self, state: WorkflowState) -> WorkflowState:
        """Analyze user input to determine intent"""
        analysis_result = self.user_input_agent.analyze_input(state.user_input)
        state.user_input_type = analysis_result["type"]
        print(f"📝 User input classified as: {state.user_input_type.value}")
        return state

    def gather_data(self, state: WorkflowState) -> WorkflowState:
        """Gather campaign data"""
        data_agent = DataGatheringAgent()
        campaign_id = "CAMPAIGN123"
        campaign_data = data_agent.gather_campaign_context(campaign_id)
        print(f"\n📊 Campaign data gathered.")
        state.campaign_data = campaign_data
        return state

    def analyze_data(self, state: WorkflowState) -> WorkflowState:
        """Analyze campaign data"""
        analysis_agent = AnalysisAgent(llm=self.llm)
        print("📊 Analyzing campaign data with AnalysisAgent...")

        if not state.campaign_data:
            raise ValueError("No campaign data to analyze.")

        analysis_result = analysis_agent.analyze_campaign(state.campaign_data)
        state.analysis_results = analysis_result
        print("📈 Analysis complete.")
        return state

    def generate_recommendations(self, state: WorkflowState) -> WorkflowState:
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

    def generate_summary(self, state: WorkflowState) -> WorkflowState:
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

    def route_after_analysis(self, state: WorkflowState) -> str:
        """Route to appropriate next step based on user input type"""
        if state.user_input_type == UserInputType.SUMMARY:
            return "generate_summary"
        elif state.user_input_type == UserInputType.RECOMMENDATION:
            return "generate_recommendations"
        elif state.user_input_type == UserInputType.DONE:
            return "end"
        return "generate_recommendations"  # default path