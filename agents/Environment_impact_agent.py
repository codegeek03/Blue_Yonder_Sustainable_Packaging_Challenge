from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any, List
from datetime import datetime
import getpass

class EnvironmentalImpactAgent:
    """
    An agent that analyzes the environmental impact of packaging materials
    based on multiple environmental metrics.
    """

    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "environmental_reports"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.user_login = getpass.getuser()

        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

        self.environmental_metrics = {
            "carbon_footprint": {"description": "CO2 emissions during production and disposal", "max_score": 10},
            "water_impact": {"description": "Water consumption and pollution during manufacturing", "max_score": 10},
            "biodegradability": {"description": "Time and conditions required for decomposition", "max_score": 10},
            "recycling_efficiency": {"description": "Ease and energy efficiency of recycling process", "max_score": 10},
            "resource_depletion": {"description": "Impact on natural resource consumption", "max_score": 10},
            "toxicity": {"description": "Potential harmful effects on ecosystems", "max_score": 10}
        }

    def get_formatted_timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _load_materials_report(self, product_name: str) -> Dict[str, Any]:
        filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        filepath = os.path.join("material_reports", filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Materials report not found for {product_name}")

    def _save_report_to_file(self, data: Dict[str, Any], product_name: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{product_name.replace(' ', '_')}_environmental_report.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filepath

    async def analyze_environmental_impact(self, product_name: str) -> Dict[str, Any]:
        materials_data = self._load_materials_report(product_name)

        prompt = f"""
You are an environmental scoring engine.

Task: For the product "{product_name}", score each material strictly (1–10) across fixed metrics.

Materials:
{json.dumps([m['material_name'] for m in materials_data['materials']])}

Respond ONLY with this JSON format:

{{
  "product_name": "{product_name}",
  "materials_analysis": [
    {{
      "material_name": "<material>",
      "metrics": {{
        "carbon_footprint": {{
          "score": <1-10>,
          "details": "<10-word CO2 summary>"
        }},
        "water_impact": {{
          "score": <1-10>,
          "details": "<10-word water summary>"
        }},
        "biodegradability": {{
          "score": <1-10>,
          "details": "<10-word biodegradability summary>"
        }},
        "recycling_efficiency": {{
          "score": <1-10>,
          "details": "<10-word recycling summary>"
        }},
        "resource_depletion": {{
          "score": <1-10>,
          "details": "<10-word resource summary>"
        }},
        "toxicity": {{
          "score": <1-10>,
          "details": "<10-word toxicity summary>"
        }}
      }},
      "overall_environmental_score": <float>,
    }}
  ],
  "summary": {{
    "best_performers": ["<mat1>", "<mat2>",.... "<mat10>"],
  }}
}}

Constraints:
- No suggestions or recommendations.
- No markdown, code block, or explanation.
- Only return valid JSON.
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
            analysis["analysis_timestamp"] = self.get_formatted_timestamp()
            analysis["user_login"] = self.user_login
            saved_path = self._save_report_to_file(analysis, product_name)
            analysis["report_path"] = saved_path
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Environmental analysis failed: {str(e)}",
                "product_name": product_name,
                "timestamp": self.get_formatted_timestamp(),
                "user_login": self.user_login
            }
            self._save_report_to_file(error_data, f"error_{product_name}")
            return error_data

    async def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Environmental Impact Analysis Report
==================================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Top Performing Materials (Environmental Score):
--------------------------------------------
"""
        sorted_materials = sorted(
            analysis['materials_analysis'],
            key=lambda x: x['overall_environmental_score'],
            reverse=True
        )

        for i, material in enumerate(sorted_materials[:5], 1):
            report += f"\n{i}. {material['material_name']} (Score: {material['overall_environmental_score']:.1f}/10)"
            report += f"\n   Key Metrics:"
            for metric in material['metrics']:
                report += f"\n   - {metric.replace('_', ' ').title()}: {material['metrics'][metric]['score']}/10"

        return report

async def main():
    try:
        agent = EnvironmentalImpactAgent()
        product_name = "Glass Bottle"
        print("Analyzing environmental impact... This may take a few moments.")
        analysis = await agent.analyze_environmental_impact(product_name)
        report = await agent.generate_summary_report(analysis)
        print("\nEnvironmental Impact Analysis Report:")
        print(report)
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())