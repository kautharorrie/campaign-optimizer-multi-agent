from langgraph.graph import StateGraph, END
from app.agents.user_input_analysis_agent import UserInputType
from .states import WorkflowState

class WorkflowBuilder:
    @staticmethod
    def create_workflow(agent_methods) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze_user_input", agent_methods["analyze_user_input"])
        workflow.add_node("gather_data", agent_methods["gather_data"])
        workflow.add_node("analyze_data", agent_methods["analyze_data"])
        workflow.add_node("generate_recommendations", agent_methods["generate_recommendations"])
        workflow.add_node("generate_summary", agent_methods["generate_summary"])

        # Add conditional edge after input analysis
        workflow.add_conditional_edges(
            "analyze_user_input",
            lambda state: "end" if state.user_input_type == UserInputType.DONE else "gather_data",
            {
                "gather_data": "gather_data",
                "end": END
            }
        )

        # Rest of the workflow
        workflow.add_edge("gather_data", "analyze_data")
        workflow.add_conditional_edges(
            "analyze_data",
            agent_methods["route_after_analysis"],
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