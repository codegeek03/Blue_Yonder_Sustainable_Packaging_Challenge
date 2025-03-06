from typing import Dict, List
import json
from .base import BaseAgent
from app.config import settings

class OrchestratorAgent(BaseAgent):
    async def decide(self,
                    product_name: str,
                    primary_class: str,
                    sub_materials: List[str],
                    quality_scores: Dict,
                    environmental_scores: Dict,
                    regulatory_scores: Dict,
                    logistics_scores: Dict) -> Dict:
        """Make final recommendation for specific material within primary class"""

        prompt = f"""
        As the Orchestrator, analyze all evaluations for {product_name} within the {primary_class} class:

        Sub-materials being evaluated:
        {json.dumps(sub_materials, indent=2)}

        Quality Scores:
        {json.dumps(quality_scores, indent=2)}

        Environmental Scores:
        {json.dumps(environmental_scores, indent=2)}

        Regulatory & Consumer Scores:
        {json.dumps(regulatory_scores, indent=2)}

        Logistics & Cost Scores:
        {json.dumps(logistics_scores, indent=2)}

        Weights:
        - Quality: {settings.QUALITY_WEIGHT}
        - Environmental: {settings.ENVIRONMENTAL_WEIGHT}
        - Regulatory & Consumer: {settings.REGULATORY_CONSUMER_WEIGHT}
        - Logistics & Cost: {settings.LOGISTICS_COST_WEIGHT}

        Follow this chain of thought:
        1. Calculate weighted scores for each specific material
        2. Compare total scores within {primary_class} class
        3. Analyze material-specific trade-offs
        4. Consider critical factors for {product_name}
        5. Make final material recommendation

        Return a JSON with this structure:
        {{
            "primary_class": "{primary_class}",
            "best_sub_material": "name of best specific material",
            "overall_scores": {{
                "material_name": <0-100>,
                ...
            }},
            "explanation": "detailed explanation of decision",
            "detailed_analysis": {{
                "material_name": {{
                    "quality": <score>,
                    "environmental": <score>,
                    "regulatory": <score>,
                    "logistics": <score>
                }},
                ...
            }}
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)