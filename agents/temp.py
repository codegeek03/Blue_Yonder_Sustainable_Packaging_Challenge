#input 
import json
import os
from typing import Dict, Union
JsonData = Dict[str, Union[str, int, float, Dict[str, float], Dict[str, str]]]

class ProductInput:
    def __init__(self):
        self.product_name = ""
        self.units_per_shipment = 0
        self.dimensions = {"length": 0, "width": 0, "height": 0}
        self.packaging_location = ""
        self.budget_constraint = 0.0

    def get_product_details(self):
        """Get product details from user input with validation"""
        # Product Name
        self.product_name = input("Enter Product Name: ").strip()
        while not self.product_name:
            print("Product name cannot be empty!")
            self.product_name = input("Enter Product Name: ").strip()

        # Units per shipment
        while True:
            try:
                self.units_per_shipment = int(input("Enter Units per shipment: "))
                if self.units_per_shipment <= 0:
                    print("Units must be a positive number!")
                    continue
                break
            except ValueError:
                print("Please enter a valid number!")

        # Dimensions
        print("\nEnter dimensions in centimeters:")
        dimensions_input = ["length", "width", "height"]
        for dim in dimensions_input:
            while True:
                try:
                    value = float(input(f"Enter {dim} (cm): "))
                    if value <= 0:
                        print(f"{dim.capitalize()} must be a positive number!")
                        continue
                    self.dimensions[dim] = value
                    break
                except ValueError:
                    print("Please enter a valid number!")

        # Packaging Location
        self.packaging_location = input("Enter Packaging Location: ").strip()
        while not self.packaging_location:
            print("Packaging location cannot be empty!")
            self.packaging_location = input("Enter Packaging Location: ").strip()

        # Budget Constraint
        while True:
            try:
                self.budget_constraint = float(input("Enter Budget Constraint: "))
                if self.budget_constraint <= 0:
                    print("Budget must be a positive number!")
                    continue
                break
            except ValueError:
                print("Please enter a valid number!")
        
        # Save to JSON
        self.save_to_json()

    def display_details(self):
        """Display the entered product details"""
        print("\nProduct Details:")
        print(f"Product Name: {self.product_name}")
        print(f"Units per shipment: {self.units_per_shipment}")
        print(f"Dimensions (L×W×H): {self.dimensions['length']}×{self.dimensions['width']}×{self.dimensions['height']} cm")
        print(f"Packaging Location: {self.packaging_location}")
        print(f"Budget Constraint: ${self.budget_constraint:.2f}")

    def save_to_json(self):
        """Save product details to JSON file"""
        data = {
            "product_name": self.product_name,
            "units_per_shipment": self.units_per_shipment,
            "dimensions": self.dimensions,
            "packaging_location": self.packaging_location,
            "budget_constraint": self.budget_constraint
        }
        
        filename = os.path.join("temp_KB", f"{self.product_name.lower().replace(' ', '_')}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

def main():
    product = ProductInput()
    product.get_product_details()
    product.display_details()

if __name__ == "__main__":
    main()

#consumer behaviour analyst 
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime

class ConsumerBehaviorAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Fixed timestamp and user
        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 21:34:07"

        self.agent = Agent(
            model=Gemini(id=model_id, api_key=api_key),
            markdown=enable_markdown
        )

        # Define consumer behavior metrics and their weights
        self.behavior_metrics = {
            "aesthetic_appeal": 0.20,      # Visual attractiveness and design
            "usability": 0.20,             # Ease of use and handling
            "perceived_value": 0.20,        # Consumer perception of worth
            "eco_consciousness": 0.20,      # Environmental awareness impact
            "brand_alignment": 0.20         # Fit with brand image and values
        }

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath

    async def analyze_consumer_behavior(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes consumer behavior and preferences for packaging materials.
        """
        prompt = f"""
Analyze consumer behavior patterns for packaging materials in {materials_data['product_name']}.
Focus on these aspects:

1. Aesthetic Appeal (20%) - Visual attractiveness and design potential
2. Usability (20%) - Consumer handling and practical usage
3. Perceived Value (20%) - Consumer perception of quality and worth
4. Eco-consciousness (20%) - Environmental awareness and sustainability
5. Brand Alignment (20%) - Fit with brand image and market positioning

Return a JSON object with exactly this structure:
{{
  "top_materials": [
    {{
      "material_name": "<name>",
      "consumer_metrics": {{
        "aesthetic_appeal": {{
          "score": <0-10>,
          "trend_strength": "<strong|moderate|weak>",
          "key_insight": "<brief consumer insight>"
        }},
        "usability": {{
          "score": <0-10>,
          "trend_strength": "<strong|moderate|weak>",
          "key_insight": "<brief consumer insight>"
        }},
        "perceived_value": {{
          "score": <0-10>,
          "trend_strength": "<strong|moderate|weak>",
          "key_insight": "<brief consumer insight>"
        }},
        "eco_consciousness": {{
          "score": <0-10>,
          "trend_strength": "<strong|moderate|weak>",
          "key_insight": "<brief consumer insight>"
        }},
        "brand_alignment": {{
          "score": <0-10>,
          "trend_strength": "<strong|moderate|weak>",
          "key_insight": "<brief consumer insight>"
        }}
      }},
      "overall_consumer_score": <0-10>,
      "target_demographics": ["<demographic1>", "<demographic2>"],
      "market_positioning": "<brief market position statement>"
    }}
  ],
  "consumer_trends": [
    {{
      "trend_name": "<trend name>",
      "impact_level": "<high|medium|low>",
      "relevance": "<brief relevance explanation>"
    }}
  ],
  "timestamp": "{self.current_time}",
  "user": "{self.user_login}"
}}

IMPORTANT:
- Return only the top 5 materials with highest consumer appeal
- Keep insights under 50 characters
- Include realistic trend assessments
- Focus on current market trends
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
            
            saved_path = self._save_report_to_file(analysis, "consumer_behavior")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Consumer behavior analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user": self.user_login
            }
            return error_data

    async def generate_consumer_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a concise consumer behavior report.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Consumer Behavior Analysis
========================
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Top 5 Materials by Consumer Appeal:
--------------------------------
"""
        
        for material in analysis['top_materials']:
            report += f"\n• {material['material_name']}"
            report += f"\n  Overall Consumer Score: {material['overall_consumer_score']}/10"
            report += f"\n  Consumer Metrics:"
            for metric_name, metric_data in material['consumer_metrics'].items():
                report += f"\n    - {metric_name.replace('_', ' ').title()}"
                report += f"\n      Score: {metric_data['score']}/10"
                report += f"\n      Trend: {metric_data['trend_strength']}"
                report += f"\n      Insight: {metric_data['key_insight']}"
            report += f"\n  Target Demographics: {', '.join(material['target_demographics'])}"
            report += f"\n  Market Position: {material['market_positioning']}\n"

        report += "\nKey Consumer Trends:\n-------------------"
        for trend in analysis['consumer_trends']:
            report += f"\n• {trend['trend_name']}"
            report += f"\n  Impact: {trend['impact_level']}"
            report += f"\n  Relevance: {trend['relevance']}\n"

        return report

async def main():
    try:
        # Load materials data
        with open('temp_KB/materials_by_criteria.json', 'r') as f:
            materials_data = json.load(f)

        agent = ConsumerBehaviorAgent()
        
        print("Analyzing consumer behavior... This may take a few moments.")
        analysis = await agent.analyze_consumer_behavior(materials_data)
        
        report = await agent.generate_consumer_report(analysis)
        print("\nConsumer Behavior Analysis Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

#logistics analyst
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any, List
from datetime import datetime

class LogisticCompatibilityAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 21:17:20"

        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

    async def analyze_top_logistics_materials(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplified analysis focusing only on top 5 materials for logistics.
        """
        prompt = f"""
For the product '{materials_data["product_name"]}', identify the top 5 most logistically viable materials.
Consider only:
1. Transportation durability (shock resistance, handling stress)
2. Storage efficiency (stacking, warehouse conditions)
3. Cost effectiveness (transport and storage costs)

Return a simple JSON with exactly this structure:
{{
  "top_materials": [
    {{
      "material_name": "<name>",
      "logistics_score": <1-10>,
      "primary_advantage": "<single main logistics advantage>",
      "cost_consideration": "<brief cost impact>"
    }}
  ],
  "timestamp": "{self.current_time}",
  "user": "{self.user_login}"
}}

Focus on only the best material from each major category in the input data.
Keep all text fields under 50 characters.
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
            
            # Save the analysis
            timestamp = self.current_time.replace(" ", "_").replace(":", "-")
            filename = f"logistics_top5_{timestamp}.json"
            filepath = os.path.join(self.reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2)
            
            analysis["report_path"] = filepath
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user": self.user_login
            }
            return error_data

    async def generate_brief_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a simplified report focusing only on top materials.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Logistics Compatibility Summary
============================
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Top 5 Materials for Logistics:
---------------------------
"""
        
        for material in analysis['top_materials']:
            report += f"\n• {material['material_name']}"
            report += f"\n  Score: {material['logistics_score']}/10"
            report += f"\n  Main Advantage: {material['primary_advantage']}"
            report += f"\n  Cost Impact: {material['cost_consideration']}\n"

        return report

async def main():
    try:
        # Load the materials data
        with open('temp_KB/materials_by_criteria.json', 'r') as f:
            materials_data = json.load(f)

        agent = LogisticCompatibilityAgent()
        
        print("Analyzing logistics compatibility... This may take a few moments.")
        analysis = await agent.analyze_top_logistics_materials(materials_data)
        
        report = await agent.generate_brief_report(analysis)
        print("\nLogistics Compatibility Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



#material analyst
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPropertiesAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Fixed timestamp and user
        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 21:27:30"

        self.agent = Agent(
            model=Gemini(id=model_id, api_key=api_key),
            markdown=enable_markdown
        )

        # Define key properties and their weights
        self.material_properties = {
            "mechanical_strength": {
                "weight": 0.20,
                "unit": "MPa"
            },
            "chemical_resistance": {
                "weight": 0.20,
                "unit": "pH range"
            },
            "thermal_stability": {
                "weight": 0.20,
                "unit": "°C"
            },
            "barrier_properties": {
                "weight": 0.20,
                "unit": "g/(m²·day)"
            },
            "durability": {
                "weight": 0.20,
                "unit": "years"
            }
        }

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath

    async def analyze_material_properties(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes material properties with simplified metrics and response structure.
        """
        prompt = f"""
Analyze the key properties of materials for {materials_data['product_name']}.
Focus on these properties:

1. Mechanical Strength (20%) - Tensile strength and structural integrity
2. Chemical Resistance (20%) - Resistance to various chemical environments
3. Thermal Stability (20%) - Performance across temperature range
4. Barrier Properties (20%) - Permeability to gases and moisture
5. Durability (20%) - Long-term performance and wear resistance

Return a JSON object with exactly this structure:
{{
  "top_materials": [
    {{
      "material_name": "<name>",
      "property_scores": {{
        "mechanical_strength": {{
          "value": "<numeric>",
          "unit": "MPa",
          "score": <0-10>
        }},
        "chemical_resistance": {{
          "value": "<numeric>",
          "unit": "pH range",
          "score": <0-10>
        }},
        "thermal_stability": {{
          "value": "<numeric>",
          "unit": "°C",
          "score": <0-10>
        }},
        "barrier_properties": {{
          "value": "<numeric>",
          "unit": "g/(m²·day)",
          "score": <0-10>
        }},
        "durability": {{
          "value": "<numeric>",
          "unit": "years",
          "score": <0-10>
        }}
      }},
      "overall_score": <0-10>,
      "key_strength": "<main property advantage>",
      "main_limitation": "<primary property limitation>"
    }}
  ],
  "timestamp": "{self.current_time}",
  "user": "{self.user_login}"
}}

IMPORTANT:
- Return only the top 5 materials with best overall properties
- Use realistic property values
- Keep text fields under 50 characters
- Include all properties with their units
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
            
            saved_path = self._save_report_to_file(analysis, "material_properties")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Properties analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user": self.user_login
            }
            return error_data

    async def generate_properties_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a concise material properties report.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Material Properties Analysis
==========================
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Top 5 Materials by Properties:
---------------------------
"""
        
        for material in analysis['top_materials']:
            report += f"\n• {material['material_name']}"
            report += f"\n  Overall Score: {material['overall_score']}/10"
            report += f"\n  Properties:"
            for prop_name, prop_data in material['property_scores'].items():
                report += f"\n    - {prop_name.replace('_', ' ').title()}: {prop_data['value']} {prop_data['unit']} (Score: {prop_data['score']}/10)"
            report += f"\n  Key Strength: {material['key_strength']}"
            report += f"\n  Main Limitation: {material['main_limitation']}\n"

        return report

async def main():
    try:
        # Load materials data
        with open('temp_KB/materials_by_criteria.json', 'r') as f:
            materials_data = json.load(f)

        agent = MaterialPropertiesAgent()
        
        print("Analyzing material properties... This may take a few moments.")
        analysis = await agent.analyze_material_properties(materials_data)
        
        report = await agent.generate_properties_report(analysis)
        print("\nMaterial Properties Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


#Matterial database agent
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any, List
from datetime import datetime, UTC
import getpass

class PackagingMaterialsAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Store user and time information at initialization
        self.user_login = "codegeek03"  # Hardcoded as provided
        self.current_time = "2025-04-19 03:21:35"  # Hardcoded as provided
        
        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

    def get_formatted_timestamp(self) -> str:
        """Returns the hardcoded timestamp for consistency"""
        return self.current_time

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        """
        Saves the analysis report to a file with consistent timestamp
        """
        filename = f"{report_type}.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    async def find_materials_by_criteria(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds 10 materials for each of the 5 main criteria categories.
        """
        prompt = f"""
You are a packaging materials specialist. For the product '{product_data["product_name"]}', provide 10 scientifically accurate materials for each of these 5 criteria:

1. Physical Form (Solid, prone to cracking):
   Requirements: {product_data["criteria"]["physical_form"]["explanation"]}
   Concerns: {product_data["criteria"]["physical_form"]["concerns"]}

2. Fragility (Medium):
   Requirements: {product_data["criteria"]["fragility"]["explanation"]}
   Concerns: {product_data["criteria"]["fragility"]["concerns"]}

3. Chemical Properties (Inert):
   Requirements: {product_data["criteria"]["chemical_properties"]["explanation"]}
   Concerns: {product_data["criteria"]["chemical_properties"]["concerns"]}

4. Hygiene Sensitivity (High):
   Requirements: {product_data["criteria"]["hygiene_sensitivity"]["explanation"]}
   Concerns: {product_data["criteria"]["hygiene_sensitivity"]["concerns"]}

5. Temperature Sensitivity (Moderate):
   Requirements: {product_data["criteria"]["temperature_sensitivity"]["explanation"]}
   Concerns: {product_data["criteria"]["temperature_sensitivity"]["concerns"]}

Return a JSON object in this exact format:
{{
  "materials_by_criteria": {{
    "physical_form": [
      {{
        "material_name": "<scientific name>",
        "properties": "<specific properties addressing the requirements>",
        "application": "<how it addresses the specific concerns>"
      }},
      // ... (10 materials total)
    ],
    "fragility": [
      // ... (10 materials)
    ],
    "chemical_properties": [
      // ... (10 materials)
    ],
    "hygiene_sensitivity": [
      // ... (10 materials)
    ],
    "temperature_sensitivity": [
      // ... (10 materials)
    ]
  }},
  "analysis_timestamp": "{self.current_time}",
  "user_login": "{self.user_login}",
  "product_name": "{product_data['product_name']}"
}}

Each material must be:
1. Scientifically accurate and specific (no generic terms)
2. Currently used in modern packaging
3. Relevant to the specific criterion
4. Include detailed properties and application
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
            
            # Save report
            saved_path = self._save_report_to_file(analysis, "materials_by_criteria")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_data["product_name"]
            }
            self._save_report_to_file(error_data, "error_materials_analysis")
            return error_data

    async def generate_materials_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a formatted report of the materials analysis.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Packaging Materials Analysis Report
================================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Generated by: {analysis['user_login']}

Materials by Criteria:
--------------------
"""
        
        for criterion, materials in analysis['materials_by_criteria'].items():
            report += f"\n{criterion.replace('_', ' ').title()}:\n"
            report += "-" * (len(criterion) + 1) + "\n"
            
            for idx, material in enumerate(materials, 1):
                report += f"{idx}. {material['material_name']}\n"
                report += f"   Properties: {material['properties']}\n"
                report += f"   Application: {material['application']}\n\n"

        return report

async def main():
    try:
        # Example input data
        input_data = {
            "criteria": {
                "physical_form": {
                    "explanation": "Solid",
                    "concerns": "Cracking"
                },
                "fragility": {
                    "explanation": "Medium",
                    "concerns": "Breakage"
                },
                "chemical_properties": {
                    "explanation": "Inert",
                    "concerns": "Leaching"
                },
                "hygiene_sensitivity": {
                    "explanation": "High",
                    "concerns": "Bacteria"
                },
                "temperature_sensitivity": {
                    "explanation": "Moderate",
                    "concerns": "Deformation"
                }
            },
            "product_name": "Eco-Friendly Bottle",
            "analysis_timestamp": "2025-04-19 03:21:35",
            "user_login": "codegeek03"
        }

        agent = PackagingMaterialsAgent()
        
        print("Analyzing materials by criteria... This may take a few moments.")
        analysis = await agent.find_materials_by_criteria(input_data)
        
        report = await agent.generate_materials_report(analysis)
        print("\nMaterials Analysis Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

#product analyst
import os
import json
import getpass
from typing import Dict, Any
from datetime import datetime
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv


class ProductCompatibilityAgent:
    """
    An agent that evaluates product compatibility based on specific criteria.
    """

    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        """
        Initialize the ProductCompatibilityAgent with the specified model.

        Args:
            model_id: The ID of the Gemini model to use
            enable_markdown: Whether to enable markdown output
        """
        # Load environment variables
        load_dotenv()

        # Get API key from environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Create temp_KB directory if it doesn't exist
        self.temp_dir = "temp_KB"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Store user information - hardcoded for the example
        self.user_login = "codegeek03"
        self.current_timestamp = "2025-04-19 03:00:29"

    def get_formatted_timestamp(self) -> str:
        """
        Get the hardcoded timestamp for consistency.

        Returns:
            Formatted timestamp string
        """
        return self.current_timestamp

    def _save_json_to_temp(self, data: Dict[str, Any], product_name: str) -> str:
        """
        Save the analysis data to a JSON file in the temp_KB directory.

        Args:
            data: The analysis data to save
            product_name: Name of the product being analyzed

        Returns:
            Path to the saved JSON file
        """
        filename = f"{product_name.lower().replace(' ', '_')}_compatibility_report.json"
        filepath = os.path.join(self.temp_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return filepath

    def load_input_json(self, product_name: str) -> Dict[str, Any]:
        """
        Load the input JSON from the specified file path.

        Args:
            product_name: Name of the product to generate the JSON file path.

        Returns:
            Dictionary containing the JSON data.
        """
        file_path = os.path.join("temp_KB", f"{product_name.lower().replace(' ', '_')}.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    async def analyze_product_compatibility(self, product_name: str, product_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compatibility of a product based on provided inputs and criteria.

        Args:
            product_name: Name of the product to analyze
            product_inputs: Dictionary containing product-specific inputs

        Returns:
            Dictionary containing compatibility analysis and concerns
        """
        prompt = f"""
You are a product compatibility analysis engine.

Analyze the product "{product_name}" with these specifications:
- Units per Shipment: {product_inputs.get('units_per_shipment')}
- Dimensions: L={product_inputs.get('dimensions', {}).get('length', 0)}cm, W={product_inputs.get('dimensions', {}).get('width', 0)}cm, H={product_inputs.get('dimensions', {}).get('height', 0)}cm
- Location: {product_inputs.get('packaging_location')}
- Budget: {product_inputs.get('budget_constraint')} units

Provide a strict JSON response with one-word descriptions:
{{
    "criteria": {{
        "physical_form": {{"explanation": "solid", "concerns": "fragile"}},
        "fragility": {{"explanation": "sturdy", "concerns": "breakable"}},
        "shelf_life": {{"explanation": "long", "concerns": "moisture"}},
        "chemical_properties": {{"explanation": "stable", "concerns": "reactive"}},
        "hygiene_sensitivity": {{"explanation": "clean", "concerns": "contamination"}},
        "temperature_sensitivity": {{"explanation": "stable", "concerns": "melting"}},
        "volatility_or_hazard_risk": {{"explanation": "safe", "concerns": "none"}},
        "visibility_and_display": {{"explanation": "clear", "concerns": "scratches"}},
        "quantity_and_dosage": {{"explanation": "bulk", "concerns": "overflow"}},
        "value_and_theft_sensitivity": {{"explanation": "secure", "concerns": "tampering"}}
    }},
    "product_name": "{product_name}",
    "analysis_timestamp": "{self.get_formatted_timestamp()}"
}}
"""

        try:
            # Initialize the agent with the Gemini model
            api_key = os.getenv('GOOGLE_API_KEY')
            self.agent = Agent(
                model=Gemini(
                    id="gemini-2.0-flash-exp",
                    api_key=api_key
                ),
                markdown=True,
            )

            response = await self.agent.arun(prompt)
            
            # Clean up response text
            response_text = response.content.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Ensure required structure
            if 'criteria' not in analysis:
                analysis['criteria'] = {}
                
            # Add metadata
            analysis['product_name'] = product_name
            analysis['analysis_timestamp'] = self.get_formatted_timestamp()
            analysis['user_login'] = self.user_login
            
            # Save report
            analysis['saved_path'] = self._save_json_to_temp(analysis, product_name)
            
            return analysis

        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {str(e)}")
            print(f"Response text: {response_text}")
            return {
                "error": "Failed to parse analysis JSON",
                "details": str(e),
                "raw_response": response_text
            }
        except Exception as e:
            print(f"General Error: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "details": str(e)
            }

    async def generate_report(self, product_name: str, product_inputs: Dict[str, Any]) -> str:
        """
        Generates a formatted compatibility report for a product.

        Args:
            product_name: Name of the product to analyze
            product_inputs: Dictionary containing product-specific inputs

        Returns:
            Formatted report as a string
        """
        try:
            analysis = await self.analyze_product_compatibility(product_name, product_inputs)

            if "error" in analysis:
                return f"Error analyzing {product_name}: {analysis['error']}\nDetails: {analysis.get('details', 'No additional details')}"

            report = f"""
Product Compatibility Report
==========================
Product: {analysis['product_name']}
Analysis Date: {analysis['analysis_timestamp']}
Analyzed by: {analysis['user_login']}

Product Specifications:
---------------------
Units per Shipment: {product_inputs.get('units_per_shipment')}
Dimensions (cm): {product_inputs.get('dimensions', {}).get('length')}L x {product_inputs.get('dimensions', {}).get('width')}W x {product_inputs.get('dimensions', {}).get('height')}H
Location: {product_inputs.get('packaging_location')}
Budget Constraint: {product_inputs.get('budget_constraint')} units

Detailed Analysis:
------------------"""
            
            if 'criteria' in analysis:
                for criterion, details in analysis['criteria'].items():
                    report += f"\n{criterion.replace('_', ' ').title()}:\n"
                    report += f"Explanation: {details.get('explanation', 'N/A')}\n"
                    report += f"Concerns: {details.get('concerns', 'N/A')}\n"
            else:
                report += "\nNo criteria analysis available."

            return report

        except Exception as e:
            return f"Error generating report: {str(e)}"


# Runner
async def main():
    try:
        agent = ProductCompatibilityAgent()

        # Load input JSON dynamically
        product_name = "Eco-Friendly Bottle"
        product_inputs = agent.load_input_json(product_name)

        # Get detailed analysis
        analysis = await agent.analyze_product_compatibility(product_name, product_inputs)
        print("\nDetailed Analysis:")
        print(json.dumps(analysis, indent=2))

        # Generate formatted report
        report = await agent.generate_report(product_name, product_inputs)
        print("\nFormatted Report:")
        print(report)

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


#sourcing agent
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime

class ProductionCostAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Fixed user and timestamp
        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 21:22:20"

        self.agent = Agent(
            model=Gemini(id=model_id, api_key=api_key),
            markdown=enable_markdown
        )

        # Define cost components and their weights
        self.cost_components = {
            "raw_material": 0.30,    # Base material cost
            "processing": 0.25,       # Manufacturing and processing
            "tariffs": 0.15,         # Import/Export duties
            "transport": 0.15,       # Shipping and handling
            "compliance": 0.15        # Regulatory and certification costs
        }

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath

    async def analyze_production_costs(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes production costs with simplified metrics and response structure.
        """
        prompt = f"""
Analyze production costs for materials used in {materials_data['product_name']}.
Focus on these cost components:

1. Raw Material Cost (30%) - Base material price per unit
2. Processing Cost (25%) - Manufacturing and processing expenses
3. Tariffs & Duties (15%) - Import/export fees
4. Transport Cost (15%) - Shipping and handling expenses
5. Compliance Cost (15%) - Regulatory and certification costs

Return a JSON object with exactly this structure:
{{
  "top_materials": [
    {{
      "material_name": "<name>",
      "cost_score": <0-10>,
      "base_price": "<price in USD/kg>",
      "key_costs": {{
        "raw_material": "<brief cost note>",
        "processing": "<brief cost note>",
        "tariffs": "<brief cost note>",
        "transport": "<brief cost note>",
        "compliance": "<brief cost note>"
      }},
      "total_estimated_cost": "<USD per unit>"
    }}
  ],
  "timestamp": "{self.current_time}",
  "user": "{self.user_login}"
}}

IMPORTANT:
- Return only the top 5 most cost-effective materials
- Keep cost notes under 30 characters
- Use realistic market prices
- Include all cost components
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
            
            saved_path = self._save_report_to_file(analysis, "production_costs")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Production cost analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user": self.user_login
            }
            return error_data

    async def generate_cost_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a concise production cost report.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Production Cost Analysis
======================
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Top 5 Cost-Effective Materials:
----------------------------
"""
        
        for material in analysis['top_materials']:
            report += f"\n• {material['material_name']}"
            report += f"\n  Overall Cost Score: {material['cost_score']}/10"
            report += f"\n  Base Price: {material['base_price']}"
            report += f"\n  Estimated Total Cost: {material['total_estimated_cost']}"
            report += "\n  Cost Breakdown:"
            for cost_type, note in material['key_costs'].items():
                report += f"\n    - {cost_type.replace('_', ' ').title()}: {note}"
            report += "\n"

        return report

async def main():
    try:
        # Load materials data
        with open('temp_KB/materials_by_criteria.json', 'r') as f:
            materials_data = json.load(f)

        agent = ProductionCostAgent()
        
        print("Analyzing production costs... This may take a few moments.")
        analysis = await agent.analyze_production_costs(materials_data)
        
        report = await agent.generate_cost_report(analysis)
        print("\nProduction Cost Analysis Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


#sustainaibility agent
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any, List
from datetime import datetime

class EnvironmentalImpactAgent:
    """
    Simplified agent that analyzes environmental impact of packaging materials.
    """

    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Fixed timestamp and user
        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 21:20:12"

        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            markdown=enable_markdown,
        )

        # Simplified metrics with weights
        self.environmental_metrics = {
            "carbon_footprint": 0.25,
            "recyclability": 0.25,
            "biodegradability": 0.20,
            "resource_efficiency": 0.15,
            "toxicity": 0.15
        }

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        """Saves analysis results to a JSON file."""
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath

    async def analyze_environmental_impact(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes environmental impact with simplified metrics and response structure.
        """
        prompt = f"""
Analyze the environmental impact of materials for {materials_data['product_name']}.
Consider these key metrics:
1. Carbon Footprint (25%) - CO2 emissions in production and disposal
2. Recyclability (25%) - Ease and efficiency of recycling
3. Biodegradability (20%) - Natural decomposition capability
4. Resource Efficiency (15%) - Natural resource consumption
5. Toxicity (15%) - Environmental hazard potential

Return a JSON object with exactly this structure:
{{
  "top_materials": [
    {{
      "material_name": "<name>",
      "environmental_score": <0-10>,
      "key_benefit": "<single main environmental advantage>",
      "primary_concern": "<main environmental challenge>"
    }}
  ],
  "timestamp": "{self.current_time}",
  "user": "{self.user_login}"
}}

IMPORTANT:
- Return only the top 5 most environmentally friendly materials
- Keep text fields under 50 characters
- Focus on practical environmental impacts
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
            
            saved_path = self._save_report_to_file(analysis, "environmental_impact")
            analysis["report_path"] = saved_path
            
            return analysis

        except Exception as e:
            error_data = {
                "error": f"Environmental analysis failed: {str(e)}",
                "timestamp": self.current_time,
                "user": self.user_login
            }
            return error_data

    async def generate_brief_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generates a concise environmental impact report.
        """
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report = f"""
Environmental Impact Analysis
===========================
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Top 5 Environmentally-Friendly Materials:
--------------------------------------
"""
        
        for material in analysis['top_materials']:
            report += f"\n• {material['material_name']}"
            report += f"\n  Score: {material['environmental_score']}/10"
            report += f"\n  Key Benefit: {material['key_benefit']}"
            report += f"\n  Primary Concern: {material['primary_concern']}\n"

        return report

async def main():
    try:
        # Load materials data
        with open('temp_KB/materials_by_criteria.json', 'r') as f:
            materials_data = json.load(f)

        agent = EnvironmentalImpactAgent()
        
        print("Analyzing environmental impact... This may take a few moments.")
        analysis = await agent.analyze_environmental_impact(materials_data)
        
        report = await agent.generate_brief_report(analysis)
        print("\nEnvironmental Impact Report:")
        print(report)
        
        print(f"\nFull report saved to: {analysis.get('report_path', 'Error: Report not saved')}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



