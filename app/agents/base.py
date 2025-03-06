from abc import ABC, abstractmethod
import groq
import requests
from bs4 import BeautifulSoup
from groq import Groq

# Define GROQ API key directly
GROQ_API_KEY = "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"

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

class BaseAgent(ABC):
    def __init__(self):
        self.groq_client = groq.Client(api_key=GROQ_API_KEY)

    @abstractmethod
    async def evaluate(self, *args, **kwargs):
        pass

    async def _run_groq_reasoning(self, prompt: str) -> str:
        """Run chain-of-thought reasoning using groq"""
        response = await self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content

    def _get_web_data(self, query: str) -> str:
        """Simple web search function using Wikipedia as a source"""
        try:
            # Use Wikipedia API for basic information
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "titles": query.replace(" ", "_")
                }
            )
            data = response.json()
            pages = data["query"]["pages"]
            # Get the first page content
            content = next(iter(pages.values())).get("extract", "")
            return content
        except Exception as e:
            return f"Error fetching data: {str(e)}"