import json
from typing import Dict, Optional
from langchain_core.tools import Tool
import wikipedia
from pathlib import Path

class DataGatheringAgent:
    def __init__(self):
        self.campaign_data_path = Path(__file__).parent.parent / "data" / "campaign_data.json"

        # Create all tools with proper binding
        self.load_campaign_data_tool = Tool(
            name="load_campaign_data",
            func=self._load_campaign_data,
            description="Loads campaign data from the mock database"
        )

        self.search_market_trends_tool = Tool(
            name="search_market_trends",
            func=self._search_market_trends,
            description="Searches for market trends based on keyword"
        )

        self.get_wikipedia_info_tool = Tool(
            name="get_wikipedia_info",
            func=self._get_wikipedia_info,
            description="Fetches relevant information from Wikipedia"
        )

    def _load_campaign_data(self, campaign_id: Optional[str] = None) -> Dict:
        """Internal method to load campaign data"""
        try:
            with open(self.campaign_data_path, 'r') as f:
                data = json.load(f)
                if campaign_id and data.get('campaign_id') != campaign_id:
                    raise ValueError(f"Campaign {campaign_id} not found")
                return data
        except Exception as e:
            raise ValueError(f"Error loading campaign data: {str(e)}")

    def _get_wikipedia_info(self, topic: str) -> str:
        """Internal method to fetch Wikipedia information"""
        try:
            print(f"Performing search for information from Wikipedia.")
            search_results = wikipedia.search(topic, results=1)
            if not search_results:
                return f"No Wikipedia information found for {topic}"

            page = wikipedia.page(search_results[0])
            return page.summary
        except Exception as e:
            return f"Error fetching Wikipedia info: {str(e)}"

    def _search_market_trends(self, keyword: str) -> str:
        """Internal method to search market trends"""
        mock_trends = {
            "fintech": "Growing adoption of digital payments, rise in mobile banking",
            "ecommerce": "Increased mobile shopping, social commerce growth",
            "digital marketing": "Focus on personalization, rise of video content",
            "social media": "Short-form video dominance, increased ad spend",
        }
        return mock_trends.get(keyword.lower(), "No trend data available")

    def gather_campaign_context(self, campaign_id: str):
        """Gathers all relevant context for a campaign"""
        campaign_data = self.load_campaign_data_tool.invoke({"campaign_id": campaign_id})

        # Enrich with market context
        if "name" in campaign_data:
            campaign_name = campaign_data.get('name').lower()
            print(f"🔍 Gathering context for campaign: {campaign_name}")

            if "fintech" in campaign_name:
                market_trends = self.search_market_trends_tool.invoke({"keyword": "fintech"})
                wiki_info = self.get_wikipedia_info_tool.invoke({"topic": "Financial technology"})
            elif "ecommerce" in campaign_name:
                market_trends = self.search_market_trends_tool.invoke({"keyword": "ecommerce"})
                wiki_info = self.get_wikipedia_info_tool.invoke({"topic": "E-commerce"})
            else:
                market_trends = self.search_market_trends_tool.invoke({"keyword": "digital marketing"})
                wiki_info = self.get_wikipedia_info_tool.invoke({"topic": "Digital marketing"})

            # Add context to campaign data
            campaign_data["market_context"] = {
                "trends": market_trends,
                "background": wiki_info
            }

        return campaign_data
