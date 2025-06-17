# Campaign Agent Platform - AI-Powered Marketing Campaign Analysis and Optimization

The Campaign Agent Platform is an intelligent system that analyzes marketing campaign performance, provides actionable recommendations, and generates comprehensive summaries using a multi-agent architecture powered by Large Language Models (LLMs).

This platform helps marketing teams optimize their campaigns by automatically analyzing key performance metrics, detecting concerning patterns, providing data-driven recommendations, and generating insightful summaries. It leverages a modular agent-based architecture to break down complex campaign analysis into specialized tasks handled by different agents.

The platform features:
- Automated analysis of campaign metrics (CTR, CPC, ROI, conversion rates)
- Pattern detection for identifying performance issues
- Contextual recommendations based on historical data and market trends
- Interactive conversation management for refining insights
- Integration with external data sources for market research
- Comprehensive campaign performance summaries

## Repository Structure
```
campaign-agent-platform/
├── agents/                     # Specialized AI agents for different tasks
│   ├── analysis_agent.py      # Analyzes campaign metrics and patterns
│   ├── data_gathering_agent.py # Collects campaign and market data
│   ├── recommendation_agent.py # Generates optimization recommendations
│   ├── summary_agent.py       # Creates comprehensive summaries
│   └── user_input_analysis_agent.py # Analyzes user requests
├── orchestrator/              # Coordinates agent interactions
│   ├── agent_handlers.py      # Manages agent execution flow
│   ├── orchestrator_v2.py     # Main orchestration logic
│   ├── workflow.py           # Defines workflow steps
│   └── states.py             # Workflow state management
├── services/                  # Application services
│   └── interactive_session.py # Manages user interaction sessions
├── utils/                     # Utility modules
│   ├── conversation_manager.py # Handles conversation state
│   └── llm.py                # LLM initialization and configuration
├── data/                      # Campaign data storage
│   ├── campaign_data.json    # Sample campaign data
│   └── campaigns.csv         # Campaign metrics database
└── cli.py                    # Command-line interface
```

## Usage Instructions
### Prerequisites
- Python 3.12 or higher
- Google API key for LLM access
- Required Python packages:
  - langchain
  - langchain-google-genai
  - rich (for CLI formatting)
  - python-dotenv

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd campaign-agent-platform
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

### Quick Start
1. Start the CLI interface:
```bash
python cli.py
```

2. Enter campaign analysis commands:
```
analyze campaign CAMPAIGN123
```

3. Request recommendations:
```
recommend improvements
```

### More Detailed Examples
1. Analyzing campaign performance:
```python
from agents.analysis_agent import AnalysisAgent
agent = AnalysisAgent()
results = agent.analyze_campaign({
    "campaign_id": "CAMPAIGN123",
    "clicks": 2543,
    "impressions": 43290,
    "spend": 9500,
    "revenue": 17500
})
```

2. Generating recommendations:
```python
from agents.recommendation_agent import RecommendationAgent
agent = RecommendationAgent()
recommendations = agent.generate_recommendations(
    campaign_data,
    analysis_results,
    conversation_history
)
```

### Troubleshooting
1. LLM Connection Issues:
- Verify Google API key is set correctly in .env
- Check network connectivity
- Ensure API quota limits haven't been exceeded

2. Data Loading Errors:
- Verify campaign_data.json exists in the data directory
- Check JSON file format is valid
- Ensure file permissions are correct

## Data Flow
The platform processes campaign data through a pipeline of specialized agents that analyze, recommend, and summarize campaign performance.

```ascii
User Input → Input Analysis → Data Gathering → Analysis → Recommendations/Summary
     ↑                                            |              |
     └────────────────── Feedback ───────────────┴──────────────┘
```

Key component interactions:
1. User input is analyzed to determine intent (summary/recommendations)
2. Data gathering agent collects campaign metrics and market context
3. Analysis agent processes metrics and detects patterns
4. Recommendation agent generates optimization suggestions
5. Summary agent creates comprehensive performance reports
6. Conversation manager maintains context across interactions
7. Orchestrator coordinates the flow between agents
8. CLI provides user interface and displays formatted results