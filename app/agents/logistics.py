from typing import Dict
import json
from .base import BaseAgent

class LogisticsAgent(BaseAgent):
    async def evaluate(self, packaging_classes: Dict[str, str]) -> Dict[str, Dict]:
        """Evaluate logistics and cost aspects"""

        # Get latest logistics and cost data
        cost_data = await self.tavily_client.search(
            query="packaging materials logistics costs supply chain efficiency",
            search_depth="advanced"
        )

        prompt = f"""
        As a Logistics & Cost Specialist, evaluate these packaging materials:

        Materials to evaluate:
        {json.dumps(packaging_classes, indent=2)}

        Consider this logistics and cost data:
        {json.dumps(cost_data, indent=2)}

        Follow this chain of thought for each material:
        1. Calculate transportation efficiency
        2. Evaluate storage requirements
        3. Assess raw material costs
        4. Analyze production scalability
        5. Consider supply chain reliability

        Return a JSON object with this exact structure:
        {{
            "material_name": {{
                "log_cost_score": <0-100>,
                "details": "detailed logistics and cost assessment"
            }},
            ...
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)