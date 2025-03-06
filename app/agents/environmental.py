from typing import Dict, List
import json
from .base import BaseAgent

class EnvironmentalAgent(BaseAgent):
    async def evaluate(self, 
                      primary_class: str, 
                      sub_materials: List[str]) -> Dict[str, Dict]:
        """Evaluate environmental impact of specific materials"""

        env_data = await self.tavily_client.search(
            query=f"environmental impact {primary_class} packaging materials specific types",
            search_depth="advanced"
        )

        prompt = f"""
        As an Environmental Impact Specialist, evaluate these specific materials 
        within the {primary_class} class:

        Materials to evaluate:
        {json.dumps(sub_materials, indent=2)}

        Consider this environmental data:
        {json.dumps(env_data, indent=2)}

        Follow this chain of thought for each specific material:
        1. Calculate specific carbon footprint
        2. Assess recyclability within {primary_class} category
        3. Evaluate material-specific biodegradability
        4. Consider specific resource consumption
        5. Analyze end-of-life environmental impact

        Return a JSON object with this structure:
        {{
            "material_name": {{
                "env_score": <0-100>,
                "details": "detailed environmental assessment specific to material type"
            }},
            ...
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)