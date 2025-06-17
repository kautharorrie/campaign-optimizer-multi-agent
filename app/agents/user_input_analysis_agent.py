from enum import Enum
from typing import Dict
from langchain_core.messages import HumanMessage
from app.utils.llm import LLMInitializer

class UserInputType(Enum):
    SUMMARY = "SUMMARY"
    RECOMMENDATION = "RECOMMENDATION"
    OTHER = "OTHER"
    DONE = "DONE"

class UserInputAnalysisAgent:
    def __init__(self, llm=None):
        self.llm = llm or LLMInitializer().llm

    def analyze_input(self, user_input: str) -> Dict:
        """
        Analyzes user input and classifies it into a specific type
        """
        if not user_input:
            return {
                "type": UserInputType.OTHER,
                "confidence": 1.0,
                "explanation": "No user input provided"
            }

        prompt = f"""
        Analyze the following user input and classify it as one of these categories:
        - SUMMARY: User wants a summary or analysis of the campaign
        - RECOMMENDATION: User wants specific recommendations or improvements
        - DONE: User indicates they are finished or satisfied
        - OTHER: Any other type of input

        Examples:
        - "Show me the campaign performance" → SUMMARY
        - "What should we improve?" → RECOMMENDATION
        - "That's all, thanks!" → DONE
        - "Can you explain this?" → OTHER

        User Input: {user_input}

        Provide your response in this format:
        TYPE: [SUMMARY/RECOMMENDATION/DONE/OTHER]
        CONFIDENCE: [0-1]
        EXPLANATION: [brief explanation]
        """

        print("🤖 Analyzing user input...")
        response = self.llm.invoke([HumanMessage(content=prompt.format(input=user_input))])

        try:
            # Parse LLM response
            lines = response.content.strip().split('\n')
            result = {
                "type": UserInputType.OTHER,  # default
                "confidence": 0.5,  # default
                "explanation": "",
                "original_input": user_input
            }

            for line in lines:
                if line.startswith('TYPE:'):
                    type_str = line.replace('TYPE:', '').strip().upper()
                    result["type"] = UserInputType[type_str]
                elif line.startswith('CONFIDENCE:'):
                    result["confidence"] = float(line.replace('CONFIDENCE:', '').strip())
                elif line.startswith('EXPLANATION:'):
                    result["explanation"] = line.replace('EXPLANATION:', '').strip()

            return result

        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            return {
                "type": UserInputType.OTHER,
                "confidence": 0.5,
                "explanation": f"Error in classification: {str(e)}",
                "original_input": user_input
            }
