from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any, List
from datetime import datetime, UTC
import getpass

class PackagingMaterialsAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Store user and time information at initialization
        self.user_login = "codegeek03"  # Hardcoded as provided
        self.current_time = "2025-04-19 03:21:35"  # Hardcoded as provided
        
        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

    def get_formatted_timestamp(self) -> str:
        """Returns the hardcoded timestamp for consistency"""
        return self.current_time

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        """
        Saves the analysis report to a file with consistent timestamp
        """
        filename = f"{report_type}.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    async def find_materials_by_criteria(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds 10 materials for each of the 5 main criteria categories.
        """
        prompt = f"""
You are a packaging materials specialist. For the product '{product_data["product_name"]}', provide 10 scientifically accurate materials for each of these 5 criteria:

1. Physical Form (Solid, prone to cracking):
   Requirements: {product_data["criteria"]["physical_form"]["explanation"]}
   Concerns: {product_data["criteria"]["physical_form"]["concerns"]}

2. Fragility (Medium):
   Requirements: {product_data["criteria"]["fragility"]["explanation"]}
   Concerns: {product_data["criteria"]["fragility"]["concerns"]}

3. Chemical Properties (Inert):
   Requirements: {product_data["criteria"]["chemical_properties"]["explanation"]}
   Concerns: {product_data["criteria"]["chemical_properties"]["concerns"]}

4. Hygiene Sensitivity (High):
   Requirements: {product_data["criteria"]["hygiene_sensitivity"]["explanation"]}
   Concerns: {product_data["criteria"]["hygiene_sensitivity"]["concerns"]}

5. Temperature Sensitivity (Moderate):
   Requirements: {product_data["criteria"]["temperature_sensitivity"]["explanation"]}
   Concerns: {product_data["criteria"]["temperature_sensitivity"]["concerns"]}

Return a JSON object in this exact format:
{{
  "materials_by_criteria": {{
    "physical_form": [
      {{
        "material_name": "<scientific name>",
        "properties": "<specific properties addressing the requirements>",
        "application": "<how it addresses the specific concerns>"
      }},
      // ... (10 materials total)
    ],
    "fragility": [
      // ... (10 materials)
    ],
    "chemical_properties": [
      // ... (10 materials)
    ],
    "hygiene_sensitivity": [
      // ... (10 materials)
    ],
    "temperature_sensitivity": [
      // ... (10 materials)
    ]
  }},
  "analysis_timestamp": "{self.current_time}",
  "user_login": "{self.user_login}",
  "product_name": "{product_data['product_name']}"
}}

Each material must be:
1. Scientifically accurate and specific (no generic terms)
2. Currently used in modern packaging
3. Relevant to the specific criterion
4. Include detailed properties and application
"""

        try:
            response = await self.agent.arun(prompt)
            
            response_text = response.content.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            analysis = json.loads(response_text)
            
            # Save report
            saved_path = self._save_report_to_file(analysis, "materials_by_criteria")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_data["product_name"]
            }
            self._save_report_to_file(error_data, "error_materials_analysis")
            return error_data

    async def generate_materials_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a formatted report of the materials analysis.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Packaging Materials Analysis Report
================================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Materials by Criteria:
--------------------
"""
        
        for criterion, materials in analysis['materials_by_criteria'].items():
            report += f"\n{criterion.replace('_', ' ').title()}:\n"
            report += "-" * (len(criterion) + 1) + "\n"
            
            for idx, material in enumerate(materials, 1):
                report += f"{idx}. {material['material_name']}\n"
                report += f"   Properties: {material['properties']}\n"
                report += f"   Application: {material['application']}\n\n"

        return report

async def main():
    try:
        # Example input data
        input_data = {
            "criteria": {
                "physical_form": {
                    "explanation": "Solid",
                    "concerns": "Cracking"
                },
                "fragility": {
                    "explanation": "Medium",
                    "concerns": "Breakage"
                },
                "chemical_properties": {
                    "explanation": "Inert",
                    "concerns": "Leaching"
                },
                "hygiene_sensitivity": {
                    "explanation": "High",
                    "concerns": "Bacteria"
                },
                "temperature_sensitivity": {
                    "explanation": "Moderate",
                    "concerns": "Deformation"
                }
            },
            "product_name": "Eco-Friendly Bottle",
            "analysis_timestamp": "2025-04-19 03:21:35",
            "user_login": "codegeek03"
        }

        agent = PackagingMaterialsAgent()
        
        print("Analyzing materials by criteria... This may take a few moments.")
        analysis = await agent.find_materials_by_criteria(input_data)
        
        report = await agent.generate_materials_report(analysis)
        print("\nMaterials Analysis Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())