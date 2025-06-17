from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.agents.user_input_analysis_agent import UserInputType

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