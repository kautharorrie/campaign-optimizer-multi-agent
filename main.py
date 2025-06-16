from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.orchestrator import OrchestratorAgent
from agents.data_gathering_agent import DataGatheringAgent
from agents.analysis_agent import AnalysisAgent
from agents.recommendation_agent import RecommendationAgent

app = FastAPI(title="Campaign Performance Optimization Assistant")

class OptimizationRequest(BaseModel):
    campaign_id: str
    user_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: str
    feedback: str

# Initialize agents
orchestrator = OrchestratorAgent()
data_gatherer = DataGatheringAgent()
analyzer = AnalysisAgent()
recommender = RecommendationAgent()

@app.post("/api/query")
async def optimize_campaign(request: OptimizationRequest) -> Dict:
    """Initiates campaign optimization process"""
    try:
        # Run through orchestrator
        result = orchestrator.run("")
        
        return {
            "status": "success",
            "campaign_id": request.campaign_id,
            "analysis": result["analysis"],
            "recommendations": result["recommendations"],
            "iterations": result["iterations"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def process_feedback(request: FeedbackRequest) -> Dict:
    """Processes feedback for recommendations"""
    try:
        # Get current state from orchestrator
        current_state = orchestrator.workflow.get_state(request.session_id)
        
        # Generate new recommendations incorporating feedback
        new_recommendations = recommender.generate_recommendations(
            current_state.campaign_data,
            current_state.analysis_results,
            request.feedback
        )
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "updated_recommendations": new_recommendations["recommendations"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)