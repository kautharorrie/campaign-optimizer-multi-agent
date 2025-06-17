from datetime import datetime
from langchain_core.messages import HumanMessage
from typing import Dict, List

from app.utils.conversation_manager import Message, MessageType
from app.utils.llm import LLMInitializer

class RecommendationAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm

    def generate_recommendations(self,
                                 campaign_data: Dict,
                                 analysis: Dict,
                                 conversation_history: List[Message] = None) -> Dict:
        """
        Generate or refine recommendations based on campaign data, analysis, and conversation history
        """
        try:
            # Customize recommendations considering conversation history
            custom_recs = self._customize_recommendations(
                campaign_data=campaign_data,
                analysis=analysis,
                conversation_history=conversation_history
            )

            # Ensure we have at least some recommendations
            if not custom_recs:
                custom_recs = ["No specific recommendations generated. Please try again."]

            return {
                "recommendations": custom_recs,
                "template_used": True,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "had_previous_interaction": bool(conversation_history),
                    "issues_addressed": analysis.get("issues", [])
                }
            }
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return {
                "recommendations": ["Unable to generate recommendations at this time."],
                "template_used": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _customize_recommendations(self,
                                   campaign_data: Dict,
                                   analysis: Dict,
                                   conversation_history: List[Message] = None):
        """
        Customize recommendations considering conversation history and user preferences
        """
        try:
            # Format conversation context
            conversation_context = self._format_conversation_history(conversation_history)

            # Safely extract values with default fallbacks
            campaign_name = campaign_data.get('name', 'Unknown')
            campaign_spend = campaign_data.get('spend', 0)
            campaign_revenue = campaign_data.get('revenue', 0)

            # Safely extract analysis data
            analysis_summary = analysis.get('analysis', '')
            market_trends = ''
            if isinstance(analysis.get('market_context'), dict):
                market_trends = analysis['market_context'].get('trends', '')
            elif isinstance(analysis.get('market_context'), str):
                market_trends = analysis['market_context']

            context = f"""
            **IMPORTANT**: Always take the user prompt into consideration when responding
            
            Conversation Context:
            {conversation_context}
            
            Campaign Context:
            - Name: {campaign_name}
            - Spend: ${campaign_spend:,.2f}
            - Revenue: ${campaign_revenue:,.2f}
            
            Analysis Summary:
            {analysis_summary}
            
            Market Context:
            {market_trends}
            
            """

            prompt = f"""
            Based on this context:
            {context}
            
            Unless otherwise specified, please provide 3 specific, actionable recommendations to improve this campaign.
            Format each recommendation as:
            
            Priority #[1-3]: [Action Item]
            - Specific steps to implement
            - Expected impact
            - Implementation timeline
            
            Note: Consider any specific requests or preferences mentioned in the conversation.
            """

            print("Making call to the LLM for recommendations...")
            response = self.llm.invoke([HumanMessage(content=prompt)])

            # Ensure we get a string response and split it into recommendations
            if response and hasattr(response, 'content'):
                recommendations = [
                    rec.strip() for rec in response.content.split("\n\n")
                    if rec.strip() and rec.strip().startswith("Priority")
                ]
                if recommendations:
                    return recommendations

        except Exception as e:
            print(f"Error in customizing recommendations: {str(e)}")
            return ["1. Review and optimize campaign settings for better performance."]

    def _format_conversation_history(self, history: List[Message]) -> str:
        """Format conversation history into useful context"""
        if not history:
            return "No previous conversation history."

        try:
            relevant_interactions = []
            for msg in history:
                if msg.type == MessageType.USER_INPUT:
                    relevant_interactions.append(f"User Prompt: {msg.content}")
                elif msg.type == MessageType.USER_FEEDBACK:
                    relevant_interactions.append(f"User Feedback: {msg.content}")
                elif msg.type == MessageType.SYSTEM_RESPONSE:
                    # Include a summarized version of system responses
                    relevant_interactions.append(f"Previous Response: {msg.content[:100]}...")

            if not relevant_interactions:
                return "No relevant conversation history found."

            formatted_history = "\n".join(relevant_interactions)

            return f"""
            Conversation Context:
            {formatted_history}
            
            Based on this history and user prompt always:
            1. Address and follow any specific requests or concerns mentioned
            2. Build upon previous suggestions if relevant
            3. Avoid repeating previous recommendations
            4. Maintain consistency in recommendation style
            """
        except Exception as e:
            print(f"Error formatting conversation history: {str(e)}")
            return "Error processing conversation history."

