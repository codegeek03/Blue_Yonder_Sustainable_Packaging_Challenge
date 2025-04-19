import os
import json
import getpass
from typing import Dict, Any
from datetime import datetime
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv


class ProductCompatibilityAgent:
    """
    An agent that evaluates product compatibility based on specific criteria.
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

        # Store user information - hardcoded for the example
        self.user_login = "codegeek03"
        self.current_timestamp = "2025-04-19 03:00:29"

    def get_formatted_timestamp(self) -> str:
        """
        Get the hardcoded timestamp for consistency.

        Returns:
            Formatted timestamp string
        """
        return self.current_timestamp

    def _save_json_to_temp(self, data: Dict[str, Any], product_name: str) -> str:
        """
        Save the analysis data to a JSON file in the temp_KB directory.

        Args:
            data: The analysis data to save
            product_name: Name of the product being analyzed

        Returns:
            Path to the saved JSON file
        """
        filename = f"{product_name.lower().replace(' ', '_')}_compatibility_report.json"
        filepath = os.path.join(self.temp_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    def load_input_json(self, product_name: str) -> Dict[str, Any]:
        """
        Load the input JSON from the specified file path.

        Args:
            product_name: Name of the product to generate the JSON file path.

        Returns:
            Dictionary containing the JSON data.
        """
        file_path = os.path.join("temp_KB", f"{product_name.lower().replace(' ', '_')}.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    async def analyze_compatibility(self, product_name: str, product_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compatibility of a product based on provided inputs and criteria.

        Args:
            product_name: Name of the product to analyze
            product_inputs: Dictionary containing product-specific inputs

        Returns:
            Dictionary containing compatibility analysis and concerns
        """
        prompt = f"""
You are a product compatibility analysis engine.

Analyze the product "{product_name}" with these specifications:
- Units per Shipment: {product_inputs.get('units_per_shipment')}
- Dimensions: L={product_inputs.get('dimensions', {}).get('length', 0)}cm, W={product_inputs.get('dimensions', {}).get('width', 0)}cm, H={product_inputs.get('dimensions', {}).get('height', 0)}cm
- Location: {product_inputs.get('packaging_location')}
- Budget: {product_inputs.get('budget_constraint')} units

Provide a strict JSON response with one-word descriptions:
{{
    "criteria": {{
        "physical_form": {{"explanation": "solid", "concerns": "fragile"}},
        "fragility": {{"explanation": "sturdy", "concerns": "breakable"}},
        "shelf_life": {{"explanation": "long", "concerns": "moisture"}},
        "chemical_properties": {{"explanation": "stable", "concerns": "reactive"}},
        "hygiene_sensitivity": {{"explanation": "clean", "concerns": "contamination"}},
        "temperature_sensitivity": {{"explanation": "stable", "concerns": "melting"}},
        "volatility_or_hazard_risk": {{"explanation": "safe", "concerns": "none"}},
        "visibility_and_display": {{"explanation": "clear", "concerns": "scratches"}},
        "quantity_and_dosage": {{"explanation": "bulk", "concerns": "overflow"}},
        "value_and_theft_sensitivity": {{"explanation": "secure", "concerns": "tampering"}}
    }},
    "product_name": "{product_name}",
    "analysis_timestamp": "{self.get_formatted_timestamp()}"
}}
"""

        try:
            # Initialize the agent with the Gemini model
            api_key = os.getenv('GOOGLE_API_KEY')
            self.agent = Agent(
                model=Gemini(
                    id="gemini-2.0-flash-exp",
                    api_key=api_key
                ),
                markdown=True,
            )

            response = await self.agent.arun(prompt)
            
            # Clean up response text
            response_text = response.content.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Ensure required structure
            if 'criteria' not in analysis:
                analysis['criteria'] = {}
                
            # Add metadata
            analysis['product_name'] = product_name
            analysis['analysis_timestamp'] = self.get_formatted_timestamp()
            analysis['user_login'] = self.user_login
            
            # Save report
            analysis['saved_path'] = self._save_json_to_temp(analysis, product_name)
            
            return analysis

        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {str(e)}")
            print(f"Response text: {response_text}")
            return {
                "error": "Failed to parse analysis JSON",
                "details": str(e),
                "raw_response": response_text
            }
        except Exception as e:
            print(f"General Error: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "details": str(e)
            }

    async def generate_report(self, product_name: str, product_inputs: Dict[str, Any]) -> str:
        """
        Generates a formatted compatibility report for a product.

        Args:
            product_name: Name of the product to analyze
            product_inputs: Dictionary containing product-specific inputs

        Returns:
            Formatted report as a string
        """
        try:
            analysis = await self.analyze_compatibility(product_name, product_inputs)

            if "error" in analysis:
                return f"Error analyzing {product_name}: {analysis['error']}\nDetails: {analysis.get('details', 'No additional details')}"

            report = f"""
Product Compatibility Report
==========================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Analyzed by: {analysis['user_login']}

Product Specifications:
---------------------
Units per Shipment: {product_inputs.get('units_per_shipment')}
Dimensions (cm): {product_inputs.get('dimensions', {}).get('length')}L x {product_inputs.get('dimensions', {}).get('width')}W x {product_inputs.get('dimensions', {}).get('height')}H
Location: {product_inputs.get('packaging_location')}
Budget Constraint: {product_inputs.get('budget_constraint')} units

Detailed Analysis:
------------------"""
            
            if 'criteria' in analysis:
                for criterion, details in analysis['criteria'].items():
                    report += f"\n{criterion.replace('_', ' ').title()}:\n"
                    report += f"Explanation: {details.get('explanation', 'N/A')}\n"
                    report += f"Concerns: {details.get('concerns', 'N/A')}\n"
            else:
                report += "\nNo criteria analysis available."

            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"


# Runner
async def main():
    try:
        agent = ProductCompatibilityAgent()

        # Load input JSON dynamically
        product_name = "Eco-Friendly Bottle"
        product_inputs = agent.load_input_json(product_name)

        # Get detailed analysis
        analysis = await agent.analyze_compatibility(product_name, product_inputs)
        print("\nDetailed Analysis:")
        print(json.dumps(analysis, indent=2))

        # Generate formatted report
        report = await agent.generate_report(product_name, product_inputs)
        print("\nFormatted Report:")
        print(report)

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())