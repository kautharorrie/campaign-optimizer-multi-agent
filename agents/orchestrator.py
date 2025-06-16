from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from tools.analyzer import analyze_campaign_performance
import os

class CampaignState(Enum):
    DATA_GATHERING = "DATA_GATHERING"
    ANALYSIS = "ANALYSIS"
    RECOMMENDATION_GENERATION = "RECOMMENDATION_GENERATION"
    IMPROVEMENT_ITERATION = "IMPROVEMENT_ITERATION"

class WorkflowState(BaseModel):
    """Tracks the state and data through the workflow"""
    current_state: CampaignState
    campaign_data: Optional[Dict] = None
    analysis_results: Optional[Dict] = None
    recommendations: Optional[List[str]] = None
    feedback: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 3

class OrchestratorAgent:
    def __init__(self):
        self.llm = self.get_llm()
        self.workflow = self._create_workflow()
        print("Initialising orch")

    def get_llm(self):
        if "GOOGLE_API_KEY" not in os.environ:
            # Only ask if not already set
            import getpass
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key: ")
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

    def _create_workflow(self) -> StateGraph:
        """Creates the LangGraph workflow for campaign optimization"""
        
        workflow = StateGraph(WorkflowState)

        # Define state transitions
        workflow.add_node("gather_data", self._gather_data)
        workflow.add_node("analyze_data", self._analyze_data)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("process_iteration", self._process_iteration)

        # Define edges
        workflow.add_edge("gather_data", "analyze_data")
        workflow.add_edge("analyze_data", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "process_iteration")
        
        # Conditional edges from iteration
        workflow.add_conditional_edges(
            "process_iteration",
            self._should_continue_iteration,
            {
                True: "gather_data",  # Loop back for more data
                False: END  # End workflow
            }
        )

        workflow.set_entry_point("gather_data")
        return workflow

    def _gather_data(self, state: WorkflowState) -> WorkflowState:
        """Gathers campaign data from available sources"""
        # For now, using mock data
        state.campaign_data = {
            "campaign_id": "CAMPAIGN123",
            "impressions": 10000,
            "clicks": 500,
            "conversions": 35,
            "revenue": 2500.00,
            "cost": 1200.00
        }
        state.current_state = CampaignState.DATA_GATHERING
        return state

    def _analyze_data(self, state: WorkflowState) -> WorkflowState:
        """Analyzes gathered campaign data"""
        if not state.campaign_data:
            raise ValueError("No campaign data available for analysis")

        analysis_result = analyze_campaign_performance(state.campaign_data)
        state.analysis_results = {"analysis": analysis_result}
        state.current_state = CampaignState.ANALYSIS
        return state

    def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        """Generates recommendations based on analysis"""
        if not state.analysis_results:
            raise ValueError("No analysis results available")

        prompt = f"""
        Based on this campaign analysis:
        {state.analysis_results['analysis']}
        
        Generate 3 specific, actionable recommendations to improve campaign performance.
        Format each recommendation as:
        1. [Action Item]: [Detailed explanation]
        """
        
        response = self.llm([HumanMessage(content=prompt)])
        state.recommendations = response.content.split("\n")
        state.current_state = CampaignState.RECOMMENDATION_GENERATION
        return state

    def _process_iteration(self, state: WorkflowState) -> WorkflowState:
        """Processes iteration feedback and updates state"""
        state.iteration_count += 1
        state.current_state = CampaignState.IMPROVEMENT_ITERATION
        return state

    def _should_continue_iteration(self, state: WorkflowState) -> bool:
        """Determines if another iteration is needed"""
        return state.iteration_count < state.max_iterations

    def run(self, user_input: str) -> Dict:
        """Runs the campaign optimization workflow"""
        initial_state = WorkflowState(
            current_state=CampaignState.DATA_GATHERING,
            iteration_count=0
        )

        # Compile and execute workflow
        compiled_workflow = self.workflow.compile()
        final_state = compiled_workflow.invoke(initial_state)


        return {
            "campaign_data": final_state.campaign_data,
            "analysis": final_state.analysis_results,
            "recommendations": final_state.recommendations,
            "iterations": final_state.iteration_count
        }

if __name__ == "__main__":
    # Instantiate the orchestrator
    orchestrator = OrchestratorAgent()

    # Simulated user input (you can extend intent detection later)
    user_input = "Can you analyse my latest campaign?"

    # Run the orchestrator workflow
    results = orchestrator.run(user_input)

    # Print the results
    print("\n🎯 Final Output:")
    print("📊 Campaign Data:")
    print(results["campaign_data"])
    print("\n🔍 Analysis:")
    print(results["analysis"])
    print("\n✅ Recommendations:")
    for rec in results["recommendations"]:
        print(rec)
    print(f"\n🔁 Total Iterations: {results['iterations']}")
