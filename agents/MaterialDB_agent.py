from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime
import getpass

class PackagingMaterialsAgent:
    """
    An agent that generates a list of 100 uniquely named, scientifically specific packaging materials for a given product.
    """

    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        """
        Initialize the PackagingMaterialsAgent with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        load_dotenv()

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "material_reports"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.user_login = getpass.getuser()

        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

    def get_formatted_timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _save_report_to_file(self, data: Dict[str, Any], product_name: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    async def analyze_packaging_materials(self, product_name: str) -> Dict[str, Any]:
        prompt = f"""
You are a strict industrial-grade packaging materials evaluator for real-world manufacturing.

Your task is to generate a list of exactly **20 uniquely named, real-world verified, and scientifically accurate packaging materials** used for the product: "{product_name}".

⚠️ STRICT NON-NEGOTIABLE RULES:

1. ✅ Each material must be **genuinely and widely used** in real-world beverage packaging (not hypothetical, rare, experimental, or for other product types).
2. ❌ DO NOT include:
   - Vague names (e.g., "plastic", "glass", "metal")
   - Overly broad categories (e.g., "fiberboard", "rubber")
   - Non-packaging materials (e.g., construction foam, electronics-grade silicone)
   - Any material **not commonly used in beverage containers, closures, liners, or labeling**.
3. ✅ Only include **technical, scientific, or industry-standard names** of materials.
4. ✅ For each material, include a brief 10-word **justification** for its use in beverage packaging.

🔬 REQUIRED JSON FORMAT:

{{
  "product_name": "{product_name}",
  "materials": [
    {{
      "material_name": "<scientific name>",
      "justification": "<exactly 10-word reason why used in beverage packaging>"
    }},
    ...
    {{
      "material_name": "<scientific name 20>",
      "justification": "<10-word explanation>"
    }}
  ]
}}

5. ✅ The JSON **must contain exactly 20 materials**, no more, no less.
6. ❌ DO NOT return markdown, explanations, formatting, or code blocks.
7. ✅ Return ONLY the valid JSON string.

🚫 Reject any inappropriate material like:
- "Glass" or variants unless strictly applicable to modern beverage bottling
- Any rubber or foam unless **clearly used in beverage closures**
- Composite names without real-world industrial validation

💡 If unable to produce valid 20 materials, return:
{{ "error": "Insufficient verified materials for beverage packaging generation." }}
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
                "error": f"Analysis failed: {str(e)}",
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
Packaging Materials Report
=========================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Materials List (Total: {len(analysis['materials'])}):
--------------------------------------------------
"""
        for i, material in enumerate(analysis['materials'], 1):
            report += f"{i}. {material['material_name']}\n"

        return report

async def main():
    try:
        agent = PackagingMaterialsAgent()

        product_name = "Glass Bottle"

        print("Analyzing packaging materials... This may take a few moments.")
        analysis = await agent.analyze_packaging_materials(product_name)

        report = await agent.generate_summary_report(analysis)
        print("\nMaterials Analysis Report:")
        print(report)

        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
