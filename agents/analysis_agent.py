from typing import Dict, List
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

class AnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
        self.performance_patterns = {
            "low_ctr": lambda data: (data["clicks"] / data["impressions"] < 0.02, "CTR below 2%"),
            "high_cost": lambda data: (data["spend"] / data["clicks"] > 5, "Cost per click above $5"),
            "low_roi": lambda data: ((data["revenue"] - data["spend"]) / data["spend"] < 1, "ROI below 100%"),
            "low_conversion": lambda data: (data["conversions"] / data["clicks"] < 0.05, "Conversion rate below 5%")
        }

    @tool
    def detect_patterns(self, campaign_data: Dict) -> List[str]:
        """Detects concerning patterns in campaign metrics"""
        issues = []
        for pattern_name, (check_fn, message) in self.performance_patterns.items():
            try:
                if check_fn(campaign_data)[0]:
                    issues.append(message)
            except (KeyError, ZeroDivisionError):
                continue
        return issues

    @tool
    def summarize_context(self, text: str, max_length: int = 200) -> str:
        """Summarizes long text content to prevent context overflow"""
        prompt = f"""
        Summarize the following text in no more than {max_length} characters while 
        preserving the key information:

        {text}
        """
        response = self.llm([HumanMessage(content=prompt)])
        return response.content

    @tool
    def analyze_metrics(self, campaign_data: Dict) -> Dict:
        """Calculates and analyzes key performance metrics"""
        try:
            metrics = {
                "ctr": (campaign_data["clicks"] / campaign_data["impressions"]) * 100,
                "conversion_rate": (campaign_data["conversions"] / campaign_data["clicks"]) * 100,
                "cost_per_click": campaign_data["spend"] / campaign_data["clicks"],
                "cost_per_conversion": campaign_data["spend"] / campaign_data["conversions"],
                "roi": ((campaign_data["revenue"] - campaign_data["spend"]) / campaign_data["spend"]) * 100
            }
            
            # Compare with targets if available
            if "target_ctr" in campaign_data:
                metrics["ctr_vs_target"] = metrics["ctr"] - (campaign_data["target_ctr"] * 100)
            if "target_roi" in campaign_data:
                metrics["roi_vs_target"] = metrics["roi"] - (campaign_data["target_roi"] * 100)
                
            return metrics
        except (KeyError, ZeroDivisionError) as e:
            raise ValueError(f"Error calculating metrics: {str(e)}")

    def analyze_campaign(self, campaign_data: Dict) -> Dict:
        """Performs comprehensive campaign analysis"""
        # Calculate metrics
        metrics = self.analyze_metrics(campaign_data)
        
        # Detect patterns/issues
        issues = self.detect_patterns(campaign_data)
        
        # Summarize market context if available
        market_context = ""
        if "market_context" in campaign_data:
            context_text = f"{campaign_data['market_context']['trends']}\n{campaign_data['market_context']['background']}"
            market_context = self.summarize_context(context_text)
        
        # Generate analysis using LLM
        prompt = f"""
        Analyze this campaign's performance:
        
        Metrics:
        {metrics}
        
        Detected Issues:
        {issues}
        
        Market Context:
        {market_context}
        
        Provide a detailed analysis focusing on:
        1. Overall performance assessment
        2. Key strengths and weaknesses
        3. Market alignment
        4. Areas needing immediate attention
        """
        
        response = self.llm([HumanMessage(content=prompt)])
        
        return {
            "metrics": metrics,
            "issues": issues,
            "market_context": market_context,
            "analysis": response.content
        }