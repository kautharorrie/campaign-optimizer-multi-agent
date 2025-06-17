from typing import Dict, List
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from app.utils.llm import LLMInitializer

class AnalysisAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm

        # Define performance patterns with tuples of (function, message)
        self.performance_patterns = {
            "low_ctr": (
                lambda data: data["clicks"] / data["impressions"] < 0.02,
                "CTR below 2%"
            ),
            "high_cost": (
                lambda data: data["spend"] / data["clicks"] > 5,
                "Cost per click above $5"
            ),
            "low_roi": (
                lambda data: (data["revenue"] - data["spend"]) / data["spend"] < 1,
                "ROI below 100%"
            ),
            "low_conversion": (
                lambda data: data["conversions"] / data["clicks"] < 0.05,
                "Conversion rate below 5%"
            )
        }

        # Create Tool instances
        self.analyze_metrics_tool = Tool(
            name="analyze_metrics",
            description="Calculates and analyzes key performance metrics",
            func=self._analyze_metrics
        )

        self.detect_patterns_tool = Tool(
            name="detect_patterns",
            description="Detects concerning patterns in campaign metrics",
            func=self._detect_patterns
        )

    def _detect_patterns(self, campaign_data: Dict) -> List[str]:
        """Internal method to detect patterns"""
        issues = []
        for pattern_name, (check_fn, message) in self.performance_patterns.items():
            try:
                if check_fn(campaign_data):  # Remove [0] as we're not returning a tuple
                    issues.append(message)
            except (KeyError, ZeroDivisionError):
                continue
        return issues

    def _analyze_metrics(self, campaign_data: Dict) -> Dict:
        """Internal method to analyze metrics"""
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
        try:
            # Calculate metrics using the tool
            metrics = self.analyze_metrics_tool.invoke({"campaign_data": campaign_data})

            # Detect patterns/issues using the tool
            issues = self.detect_patterns_tool.invoke({"campaign_data": campaign_data})

            # Summarize market context if available
            market_context = ""
            if "market_context" in campaign_data:
                if isinstance(campaign_data["market_context"], dict):
                    market_context = (f"{campaign_data['market_context'].get('trends', '')}\n"
                                  f"{campaign_data['market_context'].get('background', '')}")
                else:
                    market_context = str(campaign_data["market_context"])

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

            response = self.llm.invoke([HumanMessage(content=prompt)])

            return {
                "metrics": metrics,
                "issues": issues,
                "market_context": market_context,
                "analysis": response.content
            }

        except Exception as e:
            print(f"Error in analyze_campaign: {str(e)}")
            raise
