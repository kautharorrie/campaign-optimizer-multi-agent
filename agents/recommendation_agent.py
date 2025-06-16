import json

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool, StructuredTool, tool
from typing import Dict, List, Optional
from pydantic import BaseModel

from utils.llm import LLMInitializer


class RecommendationAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm
        self.recommendation_templates = {
            "low_ctr": """
            To improve the Click-Through Rate (CTR):
            1. [Action]: Review and optimize ad copy
               - Test different headlines and descriptions
               - Ensure clear value proposition
               - Include strong call-to-action
            
            2. [Action]: Refine targeting
               - Review audience segments
               - Analyze best performing demographics
               - Adjust bid modifiers for high-performing segments
            
            3. [Action]: Enhance ad relevance
               - Improve keyword-to-ad relevance
               - Update ad extensions
               - Consider responsive search ads
            """,

            "high_cost": """
            To reduce campaign costs:
            1. [Action]: Optimize bidding strategy
               - Review and adjust manual bids
               - Test automated bidding strategies
               - Set proper bid limits
            
            2. [Action]: Improve quality score
               - Enhance landing page experience
               - Increase ad relevance
               - Work on expected CTR
            
            3. [Action]: Refine targeting
               - Remove underperforming placements
               - Adjust demographic targeting
               - Review and update negative keywords
            """,

            "low_conversion": """
            To increase conversion rate:
            1. [Action]: Optimize landing pages
               - Improve page load speed
               - Enhance mobile experience
               - Simplify conversion process
            
            2. [Action]: Improve targeting quality
               - Focus on high-intent keywords
               - Refine audience targeting
               - Use remarketing lists
            
            3. [Action]: Enhance value proposition
               - Test different offers
               - Add social proof
               - Implement urgency elements
            """
        }

    def _generate_template_recommendations(self, issues: List[str]) -> List[str]:
        """Internal method for generating template recommendations"""
        recommendations = []
        for issue in issues:
            if "CTR" in issue:
                recommendations.append(self.recommendation_templates["low_ctr"])
            elif "Cost" in issue:
                recommendations.append(self.recommendation_templates["high_cost"])
            elif "Conversion" in issue:
                recommendations.append(self.recommendation_templates["low_conversion"])
        return recommendations

    def _customize_recommendations(self, template_recs: List[str], campaign_data: Dict, analysis: Dict) -> List[str]:
        """Internal method for customizing recommendations"""
        context = f"""
        Campaign Context:
        - Name: {campaign_data.get('name', 'Unknown')}
        - Spend: ${campaign_data.get('spend', 0):,.2f}
        - Revenue: ${campaign_data.get('revenue', 0):,.2f}
        
        Analysis Summary:
        {analysis.get('analysis', '')}
        
        Market Context:
        {analysis.get('market_context', '')}
        """

        prompt = f"""
        Given this campaign context:
        {context}
        
        And these template recommendations:
        {template_recs}
        
        Customize and prioritize these recommendations to be more specific to this campaign.
        Focus on actionable steps that align with the campaign's context and market conditions.
        Format each recommendation as:
        
        Priority #[1-3]: [Action Item]
        - Specific steps to implement
        - Expected impact
        - Implementation timeline
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.split("\n\n")

    def _incorporate_feedback(self, recommendations: List[str], feedback: str) -> List[str]:
        """Internal method for incorporating feedback"""
        prompt = f"""
        Original Recommendations:
        {recommendations}
        
        Feedback Received:
        {feedback}
        
        Please refine these recommendations considering the feedback.
        Keep the same format but adjust the content to address the feedback points.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.split("\n\n")

    def generate_recommendations(self, campaign_data: Dict, analysis: Dict, feedback: Optional[str] = None) -> Dict:
        """Main method to generate recommendations"""
        # Get template recommendations based on issues
        template_recs = self._generate_template_recommendations(analysis["issues"])

        # Customize recommendations for this campaign
        custom_recs = self._customize_recommendations(template_recs, campaign_data, analysis)

        # If feedback exists, incorporate it
        if feedback:
            final_recs = self._incorporate_feedback(custom_recs, feedback)
        else:
            final_recs = custom_recs

        return {
            "recommendations": final_recs,
            "template_used": bool(template_recs),
            "feedback_incorporated": bool(feedback)
        }

    # If you need to expose these as tools, create separate tool methods
    @tool
    def generate_template_recommendations_tool(self, issues: str) -> str:
        """Tool for generating template recommendations based on issues"""
        try:
            issues_list = issues.split(",")
            recommendations = self._generate_template_recommendations(issues_list)
            return "\n\n".join(recommendations)
        except Exception as e:
            return f"Error generating recommendations: {str(e)}"

    @tool
    def customize_recommendations_tool(self, input_str: str) -> str:
        """Tool for customizing recommendations"""
        try:
            input_data = json.loads(input_str)
            template_recs = input_data.get("template_recs", [])
            campaign_data = input_data.get("campaign_data", {})
            analysis = input_data.get("analysis", {})

            custom_recs = self._customize_recommendations(template_recs, campaign_data, analysis)
            return "\n\n".join(custom_recs)
        except Exception as e:
            return f"Error customizing recommendations: {str(e)}"
