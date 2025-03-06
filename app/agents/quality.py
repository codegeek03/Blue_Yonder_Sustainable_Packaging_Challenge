from typing import Dict, List
import json
from .base import BaseAgent

class QualityAgent(BaseAgent):
    async def evaluate(self, 
                      product_name: str,
                      primary_class: str, 
                      sub_materials: List[str]) -> Dict[str, Dict]:
        """Evaluate quality aspects of specific materials within the primary class"""
        
        prompt = f"""
        As a Quality Assessment Specialist, evaluate these specific materials 
        within the {primary_class} class for {product_name}:

        Materials to evaluate:
        {json.dumps(sub_materials, indent=2)}

        Follow this chain of thought for each specific material:
        1. Analyze material-specific durability
        2. Evaluate protection capabilities
        3. Assess shelf-life impact
        4. Consider consumer experience
        5. Examine manufacturing consistency

        Return a JSON object with this structure:
        {{
            "material_name": {{
                "quality_score": <0-100>,
                "details": "detailed quality assessment focusing on specific material properties"
            }},
            ...
        }}

        Evaluate each material based on specific properties within the {primary_class} class.
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)