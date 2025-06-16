from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agents.analysis_agent import AnalysisAgent
from agents.data_gathering_agent import DataGatheringAgent
from agents.recommendation_agent import RecommendationAgent
from agents.user_input_analysis_agent import UserInputAnalysisAgent, UserInputType
from utils.llm import LLMInitializer


class CampaignState(Enum):
    DATA_GATHERING = "DATA_GATHERING"
    ANALYSIS = "ANALYSIS"
    RECOMMENDATION_GENERATION = "RECOMMENDATION_GENERATION"
    IMPROVEMENT_ITERATION = "IMPROVEMENT_ITERATION"

class WorkflowState(BaseModel):
    current_state: CampaignState
    campaign_data: Optional[Dict] = None
    analysis_results: Optional[Dict] = None
    recommendations: Optional[List[str]] = None
    feedback: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 3
    user_input: Optional[str] = None
    user_input_type: Optional[UserInputType] = None


class OrchestratorAgent:
    def __init__(self):
        load_dotenv()
        self.workflow = self._create_workflow()
        self.llm = LLMInitializer().llm
        self.user_input_agent = UserInputAnalysisAgent(self.llm)

    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze_user_input", self._analyze_user_input)
        workflow.add_node("gather_data", self._gather_data)
        workflow.add_node("analyze_data", self._analyze_data)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        # workflow.add_node("generate_summary", self._generate_summary)

        # Define the flow
        # 1. Start with user input analysis
        workflow.add_edge("analyze_user_input", "gather_data")

        # 2. Gather data always goes to analysis
        workflow.add_edge("gather_data", "analyze_data")

        # 3. After analysis, route based on initial user input type
        workflow.add_conditional_edges(
            "analyze_data",
            self._route_after_analysis,
            {
                UserInputType.SUMMARY: "generate_summary",  # For summary, we end after analysis
                UserInputType.RECOMMENDATION: "generate_recommendations",
                UserInputType.OTHER: "generate_recommendations",
                UserInputType.DONE: END
            }
        )

        # 4. Recommendations end the workflow
        workflow.add_edge("generate_recommendations", END)
        workflow.add_edge("generate_summary", END)

        # Set the entry point
        workflow.set_entry_point("analyze_user_input")
        return workflow

    def _analyze_user_input(self, state: WorkflowState) -> WorkflowState:
        """Use UserInputAnalysisAgent to analyze the input"""
        analysis_result = self.user_input_agent.analyze_input(state.user_input)
        state.user_input_type = analysis_result["type"]
        print(f"📝 User input classified as: {state.user_input_type.value}")
        return state

    def _route_after_analysis(self, state: WorkflowState) -> UserInputType:
        """Route to appropriate node based on initial user input type"""
        return state.user_input_type or UserInputType.OTHER

    def _gather_data(self, state: WorkflowState) -> WorkflowState:
        """Use DataGatheringAgent to gather and enrich campaign context"""
        data_agent = DataGatheringAgent()
        campaign_id = "CAMPAIGN123"  # You can make this dynamic later
        campaign_data = data_agent.gather_campaign_context(campaign_id)
        print(f"📊 Campaign data gathered: {campaign_data}")
        state.campaign_data = campaign_data
        state.current_state = CampaignState.DATA_GATHERING
        return state

    def _analyze_data(self, state: WorkflowState) -> WorkflowState:
        analysis_agent = AnalysisAgent(llm=self.llm)
        print("📊 Analyzing campaign data with AnalysisAgent...")

        if not state.campaign_data:
            raise ValueError("❌ No campaign data to analyze.")

        analysis_result = analysis_agent.analyze_campaign(state.campaign_data)
        state.analysis_results = analysis_result
        state.current_state = CampaignState.ANALYSIS

        print("📈 Analysis complete.")
        return state


    def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        recommendation_agent = RecommendationAgent(llm=self.llm)
        print("🔍 Generating recommendations via RecommendationAgent")

        campaign_data = state.campaign_data or {}
        analysis = state.analysis_results or {}

        # Optionally pass feedback if you want iteration/looping
        feedback = state.feedback

        rec_result = recommendation_agent.generate_recommendations(
            campaign_data=campaign_data,
            analysis=analysis,
            feedback=feedback
        )
        # print(f"Current recommendation: {state}")

        # Save recommendations back to the state
        state.recommendations = rec_result.get("recommendations", [])
        state.current_state = CampaignState.RECOMMENDATION_GENERATION
        return state

    def _process_iteration(self, state: WorkflowState) -> WorkflowState:
        print(f"🔁 Iteration {state.iteration_count + 1} complete.")
        state.iteration_count += 1
        state.current_state = CampaignState.IMPROVEMENT_ITERATION
        return state

    def _should_continue_iteration(self, state: WorkflowState) -> bool:
        print("🔍 Checking if more iterations needed...")
        return state.iteration_count < state.max_iterations

    # ---- RUN ----
    def run(self) -> Dict:
        initial_state = WorkflowState(
            current_state=CampaignState.DATA_GATHERING,
            iteration_count=0
        )
        compiled_workflow = self.workflow.compile()
        final_state = compiled_workflow.invoke(initial_state)

        return {
            "campaign_data": final_state["campaign_data"],
            "analysis": final_state["analysis_results"],
            "recommendations": final_state["recommendations"],
            "iterations": final_state["iteration_count"]
        }

if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    result = orchestrator.run()

    print("\n✅ Final Output:")
    print("📊 Campaign Data:", result["campaign_data"])
    print("📈 Analysis:", result["analysis"])
    print("✅ Recommendations:", result["recommendations"])
    print("🔁 Total Iterations:", result["iterations"])
