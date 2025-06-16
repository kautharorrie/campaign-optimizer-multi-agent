# agents/performance_agent.py

from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.analyzer import analyze_campaign_performance
import os
import getpass

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Provide your Google API Key: ")

# Use Gemini 2.0 Flash
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Register tools
tools = [analyze_campaign_performance]

# Initialize agent with tool access
performance_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # LangChain uses this to handle tool-calling logic
    verbose=True
)

if __name__ == "__main__":
    # Sample input
    campaign_data = {
        "impressions": 10000,
        "clicks": 500,
        "conversions": 35,
        "revenue": 2500.00,
        "cost": 1200.00
    }

    print("\n--- Performance Agent Output ---")
    result = performance_agent.run(f"Analyze this campaign: {campaign_data}")
    print(result)
