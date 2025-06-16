# analyzer_tool.py

from typing import Dict

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import getpass

def get_llm():
    if "GOOGLE_API_KEY" not in os.environ:
        # Only ask if not already set
        import getpass
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key: ")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@tool
def analyze_campaign_performance(campaign_data: Dict) -> str:
    """
    Analyze campaign performance using metrics and generate feedback with an LLM.
    Expects a dictionary with keys like: impressions, clicks, conversions, revenue, cost.
    """
    try:
        impressions = int(campaign_data.get("impressions", 0))
        clicks = int(campaign_data.get("clicks", 0))
        conversions = int(campaign_data.get("conversions", 0))
        revenue = float(campaign_data.get("revenue", 0))
        cost = float(campaign_data.get("cost", 0))

        ctr = (clicks / impressions) * 100 if impressions > 0 else 0
        cvr = (conversions / clicks) * 100 if clicks > 0 else 0
        roi = ((revenue - cost) / cost) * 100 if cost > 0 else 0

        summary = (
            f"Campaign Performance Summary:\n"
            f"- Impressions: {impressions}\n"
            f"- Clicks: {clicks}\n"
            f"- Conversions: {conversions}\n"
            f"- Revenue: ${revenue:.2f}\n"
            f"- Cost: ${cost:.2f}\n"
            f"- CTR: {ctr:.2f}%\n"
            f"- CVR: {cvr:.2f}%\n"
            f"- ROI: {roi:.2f}%\n"
        )

        # Let the LLM interpret these numbers
        prompt = (
            f"Here is a campaign performance summary:\n\n{summary}\n"
            "As a marketing analyst, analyze whether this campaign performed well. "
            "Provide insights on what worked and what could be improved."
        )

        llm = get_llm()

        response = llm([HumanMessage(content=prompt)])
        return f"{summary}\n\nLLM Analysis:\n{response.content}"

    except Exception as e:
        return f"Error analyzing campaign: {str(e)}"
