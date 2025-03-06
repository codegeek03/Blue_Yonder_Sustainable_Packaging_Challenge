from typing import Dict
import json
from .base import BaseAgent

class RegulatoryAgent(BaseAgent):
    async def evaluate(self, packaging_classes: Dict[str, str]) -> Dict[str, Dict]:
        """Evaluate regulatory compliance and consumer behavior"""

        # Get latest regulatory information
        reg_data = await self.tavily_client.search(
            query="packaging materials regulations compliance standards consumer preferences",
            search_depth="advanced"
        )

        prompt = f"""
        As a Regulatory & Consumer Behavior Specialist, evaluate these packaging materials:

        Materials to evaluate:
        {json.dumps(packaging_classes, indent=2)}

        Consider this regulatory and consumer data:
        {json.dumps(reg_data, indent=2)}

        Follow this chain of thought for each material:
        1. Check compliance with current regulations
        2. Assess food safety standards (if applicable)
        3. Evaluate labeling requirements
        4. Analyze consumer sentiment
        5. Consider market acceptance

        Return a JSON object with this exact structure:
        {{
            "material_name": {{
                "reg_score": <0-100>,
                "consumer_score": <0-100>,
                "details": "detailed regulatory and consumer assessment"
            }},
            ...
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)