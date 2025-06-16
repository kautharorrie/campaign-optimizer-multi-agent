# llm_initializer.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

class LLMInitializer:
    def __init__(self, model: str = "gemini-2.0-flash", temperature: float = 0.3):
        load_dotenv()
        self.model = model
        self.temperature = temperature
        self.llm = self.get_llm()

    def get_llm(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found in environment variables.")

        return ChatGoogleGenerativeAI(
            model=self.model,
            temperature=self.temperature
        )
