from typing import Dict
import json
from .base import BaseAgent

class ResearchAgent(BaseAgent):
    async def initial_research(self, product_name: str) -> Dict[str, Dict]:
        """Research primary packaging material classes"""
        
        # Get basic product information
        product_info = self._get_web_data(f"{product_name} packaging materials")

        # Use groq for analysis
        prompt = f"""
        As a Packaging Research Specialist, analyze this product and suggest packaging materials:

        Product: {product_name}
        Available Information:
        {product_info}

        Based on general packaging knowledge and this information:
        1. Identify 2-3 primary packaging material classes most suitable for {product_name}
        2. For each class, list 3-4 specific materials within that class
        3. Provide reasoning for each suggestion

        Return a JSON object with this exact structure:
        {{
            "material_classes": {{
                "class_name": {{
                    "description": "overview of this material class",
                    "sub_materials": ["specific_material_1", "specific_material_2", ...],
                    "reasoning": "why this class is suitable for the product"
                }},
                ...
            }}
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)

    async def select_primary_class(self, 
                                 product_name: str, 
                                 material_classes: Dict) -> Dict:
        """Select the best primary material class"""
        prompt = f"""
        As a Packaging Research Specialist, analyze these material classes for {product_name}:

        {json.dumps(material_classes, indent=2)}

        Follow this chain of thought:
        1. Compare each primary class's suitability
        2. Consider industry standards
        3. Evaluate basic requirements
        4. Assess general market acceptance

        Select the SINGLE BEST primary material class and return a JSON:
        {{
            "selected_class": "name of best primary class",
            "sub_materials": ["list", "of", "specific", "materials"],
            "reasoning": "detailed explanation of selection"
        }}
        """

        result = await self._run_groq_reasoning(prompt)
        return json.loads(result)