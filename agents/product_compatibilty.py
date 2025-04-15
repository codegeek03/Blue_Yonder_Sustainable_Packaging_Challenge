from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime
import getpass

class ProductCompatibilityAgent:
    """
    An agent that analyzes product compatibility based on various material properties.
    """

    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        """
        Initialize the ProductCompatibilityAgent with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        # Load environment variables
        load_dotenv()

        # Get API key from environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Create temp_KB directory if it doesn't exist
        self.temp_dir = "temp_KB"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Store user information
        self.user_login = getpass.getuser()
        
        # Initialize the agent with Gemini model
        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

        # Define the compatibility attributes and their scoring criteria
        self.attributes = {
            "barrier_properties": {
                "description": "Resistance to liquids and gases",
                "max_score": 10
            },
            "strength_durability": {
                "description": "Physical strength and durability",
                "max_score": 10
            },
            "temperature_resistance": {
                "description": "Ability to withstand temperature variations",
                "max_score": 10
            },
            "shelf_life_impact": {
                "description": "Impact on product longevity",
                "max_score": 10
            },
            "chemical_compatibility": {
                "description": "Resistance to chemical interactions",
                "max_score": 10
            }
        }

    def get_formatted_timestamp(self) -> str:
        """
        Get the current UTC timestamp in YYYY-MM-DD HH:MM:SS format.

        Returns:
            Formatted timestamp string
        """
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _save_json_to_temp(self, data: Dict[str, Any], product_name: str) -> str:
        """
        Save the analysis data to a JSON file in the temp_KB directory.

        Args:
            data: The analysis data to save
            product_name: Name of the product being analyzed

        Returns:
            Path to the saved JSON file
        """
        # Create a filename using product name, user login, and timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{product_name.replace(' ', '_')}_compatibility_report.json"
        filepath = os.path.join(self.temp_dir, filename)

        # Save the JSON data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    async def analyze_compatibility_product(self, product_name: str) -> Dict[str, Any]:
        """
        Analyzes a product's compatibility across different attributes.

        Args:
            product_name: Name of the product to analyze

        Returns:
            Dictionary containing compatibility analysis and scores
        """
        prompt = f"""
You are a compatibility analysis engine.

Your task is to return a strict JSON object with the following structure for the product "{product_name}":

{{
  "barrier_properties": {{
    "score": <integer between 1 and 10>,
    "explanation": "<detailed explanation>",
    "concerns": "<potential issues>"
  }},
  "strength_durability": {{
    "score": <integer between 1 and 10>,
    "explanation": "<detailed explanation>",
    "concerns": "<potential issues>"
  }},
  "temperature_resistance": {{
    "score": <integer between 1 and 10>,
    "explanation": "<detailed explanation>",
    "concerns": "<potential issues>"
  }},
  "shelf_life_impact": {{
    "score": <integer between 1 and 10>,
    "explanation": "<detailed explanation>",
    "concerns": "<potential issues>"
  }},
  "chemical_compatibility": {{
    "score": <integer between 1 and 10>,
    "explanation": "<detailed explanation>",
    "concerns": "<potential issues>"
  }}
}}

Only return a valid JSON string. Do not include any explanation or markdown outside the JSON. Do not format it as a code block.
"""

        try:
            # Get analysis from Gemini
            response = await self.agent.arun(prompt)

            # Clean up response if wrapped in code blocks
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse JSON
            analysis = json.loads(response_text)

            # Add metadata
            analysis["product_name"] = product_name
            analysis["analysis_timestamp"] = self.get_formatted_timestamp()
            analysis["user_login"] = self.user_login
            analysis["overall_score"] = sum(
                analysis[attr]["score"] for attr in self.attributes.keys()
            ) / len(self.attributes)

            # Save the analysis to temp_KB folder
            saved_path = self._save_json_to_temp(analysis, product_name)
            analysis["saved_path"] = saved_path

            return analysis

        except json.JSONDecodeError:
            error_data = {
                "error": "Failed to parse analysis",
                "product_name": product_name,
                "timestamp": self.get_formatted_timestamp(),
                "user_login": self.user_login
            }
            self._save_json_to_temp(error_data, f"error_{product_name}")
            return error_data
        except Exception as e:
            error_data = {
                "error": f"Analysis failed: {str(e)}",
                "product_name": product_name,
                "timestamp": self.get_formatted_timestamp(),
                "user_login": self.user_login
            }
            self._save_json_to_temp(error_data, f"error_{product_name}")
            return error_data

    async def generate_report(self, product_name: str) -> str:
        """
        Generates a formatted compatibility report for a product.

        Args:
            product_name: Name of the product to analyze

        Returns:
            Formatted report as a string
        """
        analysis = await self.analyze_product(product_name)

        if "error" in analysis:
            return f"Error analyzing {product_name}: {analysis['error']}"

        report = f"""
Product Compatibility Report
==========================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Analyzed by: {analysis['user_login']}
Overall Score: {analysis['overall_score']:.1f}/10

Detailed Analysis:
------------------"""
        
        for attr in self.attributes.keys():
            if attr in analysis:
                report += f"\n{attr.replace('_', ' ').title()}:\n"
                report += f"Score: {analysis[attr]['score']}/10\n"
                report += f"Analysis: {analysis[attr]['explanation']}\n"
                report += f"Concerns: {analysis[attr]['concerns']}\n"

        return report


# Runner
async def main():
    try:
        # Create an instance of the agent
        agent = ProductCompatibilityAgent()

        # Example product to analyze
        product_name = "Glass Bottle"

        # Get detailed analysis
        analysis = await agent.analyze_compatibility_product(product_name)
        print("\nDetailed Analysis:")
        print(json.dumps(analysis, indent=2))

        # Generate formatted report
        report = await agent.generate_report(product_name)
        print("\nFormatted Report:")
        print(report)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())