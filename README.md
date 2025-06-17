# AI-Powered Campaign Analysis and Recommendation Platform

A modular Python-based platform that analyzes marketing campaign performance and provides data-driven recommendations through an interactive conversational interface. The platform combines data analysis, natural language processing, and machine learning to deliver actionable insights and personalized recommendations for campaign optimization.

The platform uses a multi-agent architecture to break down complex campaign analysis tasks into specialized components that work together to gather data, analyze performance metrics, generate recommendations, and provide summaries through natural conversation. It leverages language models to provide contextual understanding and natural language generation capabilities.

Key features include:
- Interactive conversational interface for campaign analysis
- Automated gathering and analysis of campaign performance metrics
- Data-driven recommendations based on performance patterns
- Contextual awareness through conversation history
- Customizable analysis and recommendation generation
- Support for multiple campaign types and metrics

## Repository Structure
```
.
├── __init__.py                     # Package initialization and session management
├── analysis_agent.py              # Analyzes campaign metrics and performance patterns
├── data_gathering_agent.py        # Gathers campaign data and market context
├── interactive_session.py         # Manages conversation flow and user interactions  
├── orchestrator_v2.py            # Coordinates workflow between different agents
├── recommendation_agent.py        # Generates customized recommendations
├── summary_agent.py              # Creates campaign performance summaries
└── user_input_analysis_agent.py  # Analyzes user intent from natural language input
```

## Usage Instructions
### Prerequisites
- Python 3.8+
- Required Python packages:
  - langchain
  - pydantic
  - python-dotenv
  - langgraph

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd campaign-agent-platform

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations
```

### Quick Start
```python
from interactive_session import InteractiveSession

# Initialize session
session = InteractiveSession()
session_id = session.start_session()

# Example interaction
response = session.process_message(
    session_id,
    "Can you analyze our campaign performance?"
)
print(response)
```

### More Detailed Examples
```python
# Get campaign recommendations
response = session.process_message(
    session_id,
    "What recommendations do you have for improving our CTR?"
)

# Get performance summary
response = session.process_message(
    session_id,
    "Can you summarize our campaign performance?"
)

# Provide feedback
response = session.process_message(
    session_id,
    "The last recommendation about social media timing didn't work for us"
)
```

### Troubleshooting
Common issues and solutions:

1. Language Model API Connection Issues
```python
# Check if API key is properly set
import os
print(os.getenv("OPENAI_API_KEY"))  # Should show your API key
```

2. Data Loading Errors
- Ensure campaign data file exists in the correct location
- Verify JSON format of campaign data
- Check file permissions

3. Memory Issues
- Monitor conversation history size
- Clear session if needed:
```python
session.clear_session(session_id)
```

## Data Flow
The platform processes campaign data through a series of specialized agents that work together to provide insights and recommendations.

```ascii
User Input → Input Analysis → Data Gathering → Analysis → Recommendations/Summary → Response
     ↑                                                           |
     |_________________________________________________________|
              Feedback Loop
```

Key component interactions:
1. User input is analyzed for intent classification
2. Relevant campaign data and context is gathered
3. Performance metrics are calculated and analyzed
4. Patterns and issues are detected
5. Recommendations or summaries are generated based on analysis
6. Response is formatted and delivered to user
7. User feedback is incorporated into future recommendations
8. Conversation history provides context for future interactions