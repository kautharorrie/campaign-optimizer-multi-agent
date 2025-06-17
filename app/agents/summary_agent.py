from typing import Dict, List
from datetime import datetime
from langchain_core.messages import HumanMessage
from app.utils.llm import LLMInitializer
from app.utils.conversation_manager import Message, MessageType

class SummaryAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm

    def generate_summary(self,
                         campaign_data: Dict,
                         analysis_results: Dict,
                         conversation_history: List[Message] = None) -> Dict:
        """
        Generate a summary based on campaign data, analysis, and conversation history
        """
        try:
            # Format conversation context
            conversation_context = self._format_conversation_history(conversation_history)

            # Prepare context
            context = self._prepare_summary_context(
                campaign_data=campaign_data,
                analysis_results=analysis_results,
                conversation_context=conversation_context
            )

            # Generate summary
            summary = self._generate_summary_content(context)

            return {
                "content": summary,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "had_previous_interaction": bool(conversation_history)
                }
            }

        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            print(f"Full error details: ", e)
            return {
                "content": "Unable to generate summary at this time.",
                "error": str(e)
            }

    def _format_conversation_history(self, history: List[Message]) -> str:
        """Format conversation history into useful context"""
        if not history:
            return "No previous conversation history."

        relevant_interactions = []
        for msg in history:
            if msg.type == MessageType.USER_INPUT:
                relevant_interactions.append(f"User Request: {msg.content}")
            elif msg.type == MessageType.SYSTEM_RESPONSE:
                relevant_interactions.append(f"Previous Response: {msg.content[:100]}...")

        return "\n".join(relevant_interactions)

    def _prepare_summary_context(self,
                                 campaign_data: Dict,
                                 analysis_results: Dict,
                                 conversation_context: str) -> str:
        """Prepare context for summary generation"""
        try:
            # Safely extract market context
            market_context = ""
            if isinstance(analysis_results.get('market_context'), dict):
                market_context = analysis_results['market_context'].get('trends', '')
            elif isinstance(analysis_results.get('market_context'), str):
                market_context = analysis_results['market_context']

            # Calculate CTR safely
            impressions = campaign_data.get('impressions', 0)
            clicks = campaign_data.get('clicks', 0)
            ctr = (clicks / impressions * 100) if impressions > 0 else 0

            context = f"""
            Campaign Information:
            - Name: {campaign_data.get('name', 'Unknown Campaign')}
            - Performance Metrics:
              * Spend: ${campaign_data.get('spend', 0):,.2f}
              * Revenue: ${campaign_data.get('revenue', 0):,.2f}
              * CTR: {ctr:.2f}%
              * Conversions: {campaign_data.get('conversions', 0)}

            Analysis Results:
            {analysis_results.get('analysis', 'No analysis available')}

            Market Context:
            {market_context}

            Recent Conversation History:
            {conversation_context}
            """

            return context

        except Exception as e:
            print(f"Error preparing summary context: {str(e)}")
            # Return a basic context if there's an error
            return f"""
            Campaign Information:
            - Name: {campaign_data.get('name', 'Unknown Campaign')}
            
            Recent Conversation History:
            {conversation_context}
            """

    def _generate_summary_content(self, context: str) -> str:
        """Generate the actual summary content"""
        try:
            prompt = f"""
            Based on the following campaign context:
            {context}

            Please provide a concise summary that includes:
            1. Key campaign performance metrics and their implications
            2. Main insights from the analysis
            3. Critical areas requiring attention
            4. Market context relevance

            Format the summary in clear, actionable paragraphs.
            """

            print("Making call to the LLM for summary...")
            response = self.llm.invoke([HumanMessage(content=prompt)])

            if response and hasattr(response, 'content'):
                return response.content.strip()

            raise ValueError("No valid response from LLM")

        except Exception as e:
            print(f"Error generating summary content: {str(e)}")
            return "Unable to generate summary content due to an error."
