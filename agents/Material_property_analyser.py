from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPropertiesAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.agent = Agent(model=Gemini(id=model_id, api_key=api_key), markdown=enable_markdown)
        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)
        self.user_login = "codegeek03"

    def _load_materials_report(self, product_name: str) -> Dict[str, Any]:
        filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        filepath = os.path.join("material_reports", filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Materials report not found for {product_name}")

    def _save_report_to_file(self, data: Dict[str, Any], product_name: str) -> str:
        filename = f"{product_name.replace(' ', '_')}_properties_report.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    def _get_timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    async def analyze_properties_properties(self, product_name: str) -> Dict[str, Any]:
        materials_data = self._load_materials_report(product_name)

        prompt = f"""
You are a materials properties scoring engine.

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
        "mechanical_strength": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "MPa",
          "details": "<10-word strength assessment>"
        }},
        "impact_resistance": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "J/m",
          "details": "<10-word impact resistance assessment>"
        }},
        "thermal_stability": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "°C",
          "details": "<10-word thermal stability assessment>"
        }},
        "chemical_resistance": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "pH range",
          "details": "<10-word chemical resistance assessment>"
        }},
        "barrier_properties": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "g/(m²·day)",
          "details": "<10-word barrier properties assessment>"
        }},
        "durability": {{
          "score": <1-10>,
          "value": "<numeric value>",
          "unit": "years",
          "details": "<10-word durability assessment>"
        }}
      }},
      "overall_property_score": <float>,
      "optimal_applications": ["<application1>", "<application2>"]
    }}
  ],
  "summary": {{
    "top_performers": ["<mat1>", "<mat2>", "<mat10>"],
    "by_property": {{
      "mechanical_strength": ["<mat1>", "<mat2>", "<mat3>"],
      "impact_resistance": ["<mat1>", "<mat2>", "<mat3>"],
      "thermal_stability": ["<mat1>", "<mat2>", "<mat3>"],
      "chemical_resistance": ["<mat1>", "<mat2>", "<mat3>"],
      "barrier_properties": ["<mat1>", "<mat2>", "<mat3>"],
      "durability": ["<mat1>", "<mat2>", "<mat3>"]
    }}
  }}
}}

Constraints:
- No suggestions or recommendations.
- No markdown, code block, or explanation.
- Only return valid JSON.
- All numeric values must be realistic for packaging materials.
- Units must match those specified in the template.
"""

        try:
            response = await self.agent.arun(prompt)
            response_text = response.content.strip()
            for tag in ["```json", "```"]:
                if response_text.startswith(tag): response_text = response_text[len(tag):]
                if response_text.endswith(tag): response_text = response_text[:-len(tag)]

            analysis = json.loads(response_text)
            analysis["analysis_timestamp"] = self._get_timestamp()
            analysis["user_login"] = self.user_login
            analysis["report_path"] = self._save_report_to_file(analysis, product_name)
            return analysis

        except Exception as e:
            error = {
                "error": f"Material properties analysis failed: {str(e)}",
                "product_name": product_name,
                "timestamp": self._get_timestamp(),
                "user_login": self.user_login
            }
            self._save_report_to_file(error, f"error_{product_name}")
            return error

    async def generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Material Properties Analysis Report
===================================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Top Materials (Overall Score):
------------------------------
"""
        sorted_mats = sorted(analysis['materials_analysis'], key=lambda x: x['overall_property_score'], reverse=True)
        for i, mat in enumerate(sorted_mats[:5], 1):
            report += f"\n{i}. {mat['material_name']} (Score: {mat['overall_property_score']:.1f}/10)"
            for metric, data in mat['metrics'].items():
                report += f"\n   - {metric.replace('_', ' ').title()}: {data['score']}/10 ({data['value']} {data['unit']})"
            report += f"\n   Optimal Applications: {', '.join(mat['optimal_applications'])}\n"

        report += "\nTop Performers by Property:\n----------------------------"
        for prop, mats in analysis['summary']['by_property'].items():
            report += f"\n{prop.replace('_', ' ').title()}: {', '.join(mats[:3])}"

        return report

# --- Script Entry Point ---
async def main():
    try:
        agent = MaterialPropertiesAgent()
        product_name = "Glass Bottle"
        print("Analyzing material properties...")
        analysis = await agent.analyze_properties_properties(product_name)
        report = await agent.generate_summary_report(analysis)
        print(report)
        print(f"\nReport saved to: {analysis.get('report_path', 'Error: Report not saved')}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
