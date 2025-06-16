# Campaign Performance Optimization Assistant

## Overview
At its core, the Campaign Performance Optimization Assistant is an AI-powered system designed to analyze the performance of digital marketing campaigns, identify areas for improvement, and generate actionable recommendations to enhance their effectiveness. It acts like an intelligent, automated marketing consultant, continuously seeking ways to make campaigns more efficient and impactful.

## Agents
### Orchestration Agent
- The role of this agent is to oversee the entire optimization process
- Decides which sub-agents to invoke
- Manages flow
- Iteratively refines the strategy
- Tools: The agent will have access to other agents outputs and will use it to refine its output 
- This agent needs to implement a clear state machine: DATA_GATHERING -> ANALYSIS -> RECOMMENDATION_GENERATION -> IMPROVEMENT_ITERATION

### Data Gathering Agent
- Gathers all relevant information for the campaign performance 
Tools: 
1. Web search (for market trends, competitor analysis, industry benchmarks)
2. Wikipedia API: for background on specific products/target demographics
3. "Mock" Database connector: Simulates fetching campaign data (for now a simple JSON is sufficient)
4. If applicable, process documents of campaign data if provided

### Analysis Agent
- The role is to interpret the gathered data, identify the strengths/weakneses and point areas of improvement
Tools:
1. Generate textual descriptions of trends based on data
2. Pattern Recognition:  A simple function that looks for keywords or data patterns
3. Use LLM prompt engineering to give the LLM proper instructions to analyse the data

### Recommendation Agent
- Formulate concrete, actionable recommendations based on analysis
Tools: 
1. Recommendation Template Tool: Ensure recommendations and follow a structured format (LLM recommendation, will be crafted using prompt engineering)
2. Iteration/ Feedback tool if applicable

## Technical Implementations
1. LangGraph for Orchestration: Leverage its state management and cyclical graph capabilities to model the iterative refinement process. Show how the Orchestration Agent can loop back to Data Gathering or Analysis based on its "Refinement Tool" feedback.
2. Efficient Context Window Management:
   1. Summarization Tool: Before passing large chunks of data to an LLM, use an LLM or a simple heuristic to summarize it.
   2. Retrieval Augmented Generation (RAG): When interacting with your "mock database" or file processor, only retrieve and pass relevant chunks of information to the LLM, not the entire dataset. 
3. Reinforcement Learning Feedback Loops 
   1. Human-in-the-Loop: After a recommendation, the "client" (you, the user) provides feedback ("This recommendation was helpful," "This was irrelevant"). The Orchestration Agent uses this feedback to refine strategies 
   2. Self-Correction: The Orchestration Agent can detect if an analysis is insufficient and autonomously request more data or a re-analysis.
4. Input Classification: determine the intent of the user's initial query and route it to the appropriate initial agent or workflow. 
5. Tool Selection: Use semantic similarity to help the agent choose the best tool for a given sub-task.
6. Incorporate memory management between client/user and orchestration to keep the conversation history as part of the process (can use mock json for now)
7. Keep states between agents 

