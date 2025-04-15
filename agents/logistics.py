from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os, json
from typing import Dict, Any
from datetime import datetime

class LogisticsCostAnalyzerAgent:
    def __init__(self, model_id="gemini-2.0-flash-exp", enable_markdown=False):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.agent = Agent(model=Gemini(id=model_id, api_key=api_key), markdown=enable_markdown)
        self.reports_dir = "logistics_cost_reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        self.user_login = "codegeek03"

    def _load_material_input(self, product_name: str) -> Dict[str, Any]:
        filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        filepath = os.path.join("material_reports", filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_report(self, data: Dict[str, Any], product_name: str) -> str:
        filename = f"{product_name.replace(' ', '_')}_logistics_cost.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    def _timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    async def analyze_logistics_costs(self, product_name: str) -> Dict[str, Any]:
        materials = self._load_material_input(product_name)

        prompt = f"""
You are a logistics cost analysis engine.

Task: For the product "{product_name}", assess each material across fixed logistics-related metrics.

Materials:
{json.dumps([m['material_name'] for m in materials['materials']])}

Respond STRICTLY in the following JSON format:

{{
  "product_name": "{product_name}",
  "logistics_analysis": [
    {{
      "material_name": "<material>",
      "metrics": {{
        "weight_density": {{
          "score": <1-10>,
          "value": "<numeric>",
          "unit": "kg/m³",
          "details": "<10-word comment>"
        }},
        "volume_efficiency": {{
          "score": <1-10>,
          "value": "<numeric>",
          "unit": "%",
          "details": "<10-word comment>"
        }},
        "stackability": {{
          "score": <1-10>,
          "value": "<numeric>",
          "unit": "rating",
          "details": "<10-word comment>"
        }},
        "transport_mode_fit": {{
          "score": <1-10>,
          "value": "<numeric>",
          "unit": "rating",
          "details": "<10-word comment>"
        }},
        "fragility_index": {{
          "score": <1-10>,
          "value": "<numeric>",
          "unit": "rating",
          "details": "<10-word comment>"
        }},
        "logistics_cost_estimate": {{
          "value": "<numeric>",
          "unit": "USD/kg",
          "details": "<10-word cost implication comment>"
        }}
      }},
      "overall_logistics_score": <float>
    }}
  ],
  "summary": {{
    "lowest_cost_materials": ["<mat1>", "<mat2>", "<mat3>"],
    "by_metric": {{
      "weight_density": ["<mat1>", "<mat2>", "<mat3>"],
      "volume_efficiency": ["<mat1>", "<mat2>", "<mat3>"],
      "stackability": ["<mat1>", "<mat2>", "<mat3>"],
      "transport_mode_fit": ["<mat1>", "<mat2>", "<mat3>"],
      "fragility_index": ["<mat1>", "<mat2>", "<mat3>"]
    }}
  }}
}}

Constraints:
- Do not suggest or recommend.
- Do not include markdown, explanation, or prose.
- All numeric values must be realistic and plausible for packaging.
- Units must strictly match the template.
"""

        try:
            response = await self.agent.arun(prompt)
            content = response.content.strip()
            for tag in ["```json", "```"]:
                if content.startswith(tag): content = content[len(tag):]
                if content.endswith(tag): content = content[:-len(tag)]

            data = json.loads(content)
            data["analysis_timestamp"] = self._timestamp()
            data["user_login"] = self.user_login
            data["report_path"] = self._save_report(data, product_name)
            return data

        except Exception as e:
            error = {
                "error": str(e),
                "timestamp": self._timestamp(),
                "user_login": self.user_login,
                "product_name": product_name
            }
            self._save_report(error, f"error_{product_name}")
            return error

# --- Example Usage ---
async def main():
    agent = LogisticsCostAnalyzerAgent()
    result = await agent.analyze_logistics_costs("Glass Bottle")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
