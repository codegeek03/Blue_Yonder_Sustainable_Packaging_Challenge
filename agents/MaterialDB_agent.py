import os
import re
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

from agno.agent import Agent
from agno.models.google import Gemini

logger = logging.getLogger(__name__)

class PackagingMaterialsAgent:
    def __init__(
        self,
        user_login: str,
        current_time: str,
        model_id: str = "gemini-2.0-flash-exp",
        enable_markdown: bool = True
    ):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.user_login = user_login
        self.current_time = current_time
        self.agent = Agent(
            model=Gemini(id=model_id, api_key=api_key),
            markdown=enable_markdown,
        )

    def get_formatted_timestamp(self) -> str:
        return self.current_time

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        path = os.path.join(self.reports_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return path

    async def find_materials_by_criteria(
        self,
        compatibility_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            criteria = compatibility_analysis.get("criteria", {})
            product_name = compatibility_analysis.get("product_name", "")

            # Build minimal JSON schema for materials_by_criteria
            schema = {
                "materials_by_criteria": {
                    key: [
                        {
                            "material_name": "string",
                            "properties": "string",
                            "application": "string"
                        }
                    ] * 10
                    for key in criteria
                },
                "analysis_timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_name
            }

            prompt = (
                f"You’re a packaging materials specialist. "
                f"For product '{product_name}', return exactly this JSON schema without extra keys:\n\n"
                f"{json.dumps(schema, indent=2)}\n\n"
                "Materials must be scientifically accurate, modern, and relevant."
            )

            # Call LLM
            response = await self.agent.arun(prompt)
            text = response.content.strip()
            # strip markdown fences
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]

            # Parse JSON with fallback for trailing commas
            try:
                analysis = json.loads(text)
            except json.JSONDecodeError:
                cleaned = re.sub(r',\s*([\]}])', r'\1', text)
                analysis = json.loads(cleaned)

            result = {
                "materials": analysis.get("materials_by_criteria", {}),
                "analysis_timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_name,
                "status": "completed"
            }

            result["report_path"] = self._save_report_to_file(result, "materials_analysis")
            return result

        except Exception as e:
            logger.error(f"Material analysis failed: {e}", exc_info=True)
            error_data = {
                "error": f"Analysis failed: {e}",
                "timestamp": self.current_time,
                "user_login": self.user_login,
                "status": "failed"
            }
            self._save_report_to_file(error_data, "error_materials_analysis")
            return error_data

    async def generate_materials_report(self, analysis: Dict[str, Any]) -> str:
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report_lines = [
            "Packaging Materials Analysis Report",
            "================================",
            f"Product: {analysis['product_name']}",
            f"Date: {analysis['analysis_timestamp']}",
            f"User: {analysis['user_login']}",
            "",
            "Materials by Criteria:",
            "---------------------",
        ]

        for crit, mats in analysis.get('materials', {}).items():
            report_lines.append(f"\n{crit.replace('_',' ').title()}:")
            for i, m in enumerate(mats, 1):
                report_lines.append(f"{i}. {m.get('material_name','')}\n   Props: {m.get('properties','')}\n   App: {m.get('application','')}")

        return "\n".join(report_lines)
