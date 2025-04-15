from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime

class MaterialCostAgent:
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
        filename = f"{product_name.replace(' ', '_')}_cost_report.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    def _get_timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    async def analyze_cost_costs(self, product_name: str) -> Dict[str, Any]:
        materials_data = self._load_materials_report(product_name)

        prompt = f"""
You are a strict JSON-only material cost analysis engine.

PRODUCT: "{product_name}"

TASK: Evaluate each material used in this product for cost-efficiency using real-world packaging economics. Each material must be scored across six cost metrics, with real units, realistic values, and consistent format.

MATERIALS TO ANALYZE (NO ADDITIONS, NO CHANGES):
{json.dumps([m['material_name'] for m in materials_data['materials']])}

STRICT RULES:
1. Respond with ONLY VALID JSON — no markdown, no extra text, no explanation.
2. Units MUST MATCH EXACTLY as defined below — NO substitutions or variations.
3. Numeric values MUST BE realistic for packaging materials, not made up.
4. Each field must be filled — DO NOT omit any fields or properties.
5. Details must be concise: strictly 10 words per metric.
6. Use only TWO sectors for "economic_suitability" per material.
7. Do NOT recommend materials — just score and describe.

STRICT FORMAT (REPRODUCE THIS EXACTLY, ONLY WITH FILLED VALUES):

{{
  "product_name": "{product_name}",
  "materials_cost_analysis": [
    {{
      "material_name": "<material>",
      "cost_metrics": {{
        "raw_material_cost": {{
          "value": "<numeric>",
          "unit": "USD/kg",
          "score": <1-10>,
          "details": "<exactly 10-word cost comment>"
        }},
        "processing_cost": {{
          "value": "<numeric>",
          "unit": "USD/unit",
          "score": <1-10>,
          "details": "<10-word comment>"
        }},
        "availability": {{
          "value": "<numeric>",
          "unit": "%",
          "score": <1-10>,
          "details": "<10-word availability comment>"
        }},
        }}
      }},
      "total_cost_score": <float>,
      "economic_suitability": ["<sector1>", "<sector2>"]
    }}
  ],
  "summary": {{
    "most_economical_materials": ["<mat1>", "<mat2>", "<mat3>"],
    "by_cost_metric": {{
      "raw_material_cost": ["<mat1>", "<mat2>", "<mat3>"],
      "processing_cost": ["<mat1>", "<mat2>", "<mat3>"],
      "availability": ["<mat1>", "<mat2>", "<mat3>"],
    }}
  }}
}}

FINAL INSTRUCTIONS:
- Output must contain NO additional commentary.
- DO NOT wrap in code blocks.
- DO NOT hallucinate new materials or sectors.
- ONLY USE the format and materials provided.
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
                "error": f"Material cost analysis failed: {str(e)}",
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
Material Cost Analysis Report
=============================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Top Economical Materials:
-------------------------
"""
        sorted_mats = sorted(analysis['materials_cost_analysis'], key=lambda x: x['total_cost_score'], reverse=True)
        for i, mat in enumerate(sorted_mats[:5], 1):
            report += f"\n{i}. {mat['material_name']} (Score: {mat['total_cost_score']:.1f}/10)"
            for metric, data in mat['cost_metrics'].items():
                report += f"\n   - {metric.replace('_', ' ').title()}: {data['score']}/10 ({data['value']} {data['unit']})"
            report += f"\n   Suitable Sectors: {', '.join(mat['economic_suitability'])}\n"

        report += "\nTop Performers by Cost Metric:\n-------------------------------"
        for prop, mats in analysis['summary']['by_cost_metric'].items():
            report += f"\n{prop.replace('_', ' ').title()}: {', '.join(mats[:3])}"

        return report

# --- Script Entry Point ---
async def main():
    try:
        agent = MaterialCostAgent()
        product_name = "Glass Bottle"
        print("Analyzing material costs...")
        analysis = await agent.analyze_cost_costs(product_name)
        report = await agent.generate_summary_report(analysis)
        print(report)
        print(f"\nReport saved to: {analysis.get('report_path', 'Error: Report not saved')}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
