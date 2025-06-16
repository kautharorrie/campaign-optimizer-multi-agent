from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from utils.llm import LLMInitializer

class SummaryAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm

    def generate_summary(self, campaign_data: Dict, analysis_results: Dict) -> Dict:
        """
        Generates a comprehensive summary of the campaign based on data and analysis
        """
        try:
            # Extract key metrics and insights
            metrics = analysis_results.get("metrics", {})
            analysis = analysis_results.get("analysis", "")
            market_context = campaign_data.get("market_context", {})

            # Create a structured prompt for the LLM
            prompt = f"""
            Generate a clear and concise summary of this marketing campaign's performance.
            
            Campaign Data:
            {campaign_data}
            
            Key Metrics:
            {metrics}
            
            Analysis:
            {analysis}
            
            Market Context:
            {market_context}
            
            Please provide a structured summary with the following sections:
            1. Campaign Overview (2-3 sentences)
            2. Key Performance Metrics (bullet points)
            3. Main Insights (2-3 key findings)
            4. Market Context (1-2 sentences)
            
            Format the response in a clear, business-friendly manner.
            """

            # Get summary from LLM
            response = self.llm([HumanMessage(content=prompt)])
            summary_text = response.content

            # Structure the summary response
            return {
                "summary": summary_text,
                "campaign_name": campaign_data.get("name", "Unnamed Campaign"),
                "key_metrics": metrics,
                "timestamp": campaign_data.get("timestamp", "Not specified"),
                "success": True
            }

        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {
                "summary": "Error generating summary",
                "error": str(e),
                "success": False
            }

    def generate_brief_summary(self, analysis_results: Dict) -> str:
        """
        Generates a brief, focused summary based only on analysis results
        """
        try:
            prompt = f"""
            Create a brief, focused summary of the campaign analysis results in 2-3 sentences.
            Focus on the most important findings and metrics.

            Analysis Results:
            {analysis_results}
            """

            response = self.llm([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            print(f"Error generating brief summary: {str(e)}")
            return f"Error generating brief summary: {str(e)}"
