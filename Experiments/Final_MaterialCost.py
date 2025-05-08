from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
import aiohttp
import asyncio
from typing import Dict, Any, List
from datetime import datetime

class PackagingCostAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.agent = Agent(model=Gemini(id=model_id, api_key=api_key), markdown=enable_markdown)
         # Get the absolute path to the existing agents folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # If this file is already in the agents folder, we can use the parent directory
        if os.path.basename(base_dir) == "agents":
            self.reports_dir = os.path.join(base_dir, "cost_final")
        else:
            # Find the agents folder from the current working directory
            project_dir = os.path.dirname(base_dir)
            self.reports_dir = os.path.join(project_dir, "agents", "cost_final")
        os.makedirs(self.reports_dir, exist_ok=True)
        self.user_login = "swara"
        
        # API keys for external data sources
        self.tariff_api_key = os.getenv("TARIFF_API_KEY")
        self.export_duty_api_key = os.getenv("EXPORT_DUTY_API_KEY")
        self.production_cost_api_key = os.getenv("PRODUCTION_COST_API_KEY")#if api key not found then ignore it

    async def fetch_production_costs(self, materials: List[str], country: str = "US") -> Dict[str, float]:
        """Fetch real-time production costs for materials from an API."""
        # In a real implementation, this would call an actual API
        # This is a mock implementation
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.productiondata.com/v1/materials/costs"
            headers = {"Authorization": f"Bearer {self.production_cost_api_key}"}
            params = {"materials": ",".join(materials), "country": country}
            
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {material: cost for material, cost in data["costs"].items()}
                    else:
                        # Fallback to mock data if API fails
                        print(f"Warning: Production cost API returned status {response.status}. Using mock data.")
            except Exception as e:
                print(f"Error fetching production costs: {str(e)}. Using mock data.")
        
        # Mock data as fallback
        return {
            "Plastic": 1.25,
            "Glass": 0.89,
            "Cardboard": 0.45,
            "Aluminum": 2.35,
            "Paper": 0.75,
            "Biodegradable Plastic": 3.15,
            "Steel": 1.85,
            "Wood": 1.05,
            "Cork": 2.75,
            "Fabric": 3.45
        }

    async def fetch_tariffs(self, materials: List[str], origin_country: str, destination_country: str) -> Dict[str, float]:
        """Fetch tariff rates for materials between countries."""
        # In a real implementation, this would call an actual API
        # This is a mock implementation
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.tradetariffs.com/v2/rates"
            headers = {"X-API-Key": self.tariff_api_key}
            params = {
                "materials": ",".join(materials),
                "origin": origin_country,
                "destination": destination_country
            }
            
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {material: rate for material, rate in data["tariff_rates"].items()}
                    else:
                        # Fallback to mock data if API fails
                        print(f"Warning: Tariff API returned status {response.status}. Using mock data.")
            except Exception as e:
                print(f"Error fetching tariffs: {str(e)}. Using mock data.")
        
        # Mock data as fallback (percentage rates)
        return {
            "Plastic": 5.5,
            "Glass": 7.0,
            "Cardboard": 3.0,
            "Aluminum": 8.5,
            "Paper": 2.5,
            "Biodegradable Plastic": 2.0,
            "Steel": 6.5,
            "Wood": 4.5,
            "Cork": 3.5,
            "Fabric": 9.0
        }

    async def fetch_export_duties(self, materials: List[str], origin_country: str) -> Dict[str, float]:
        """Fetch export duty rates for materials from the origin country."""
        # In a real implementation, this would call an actual API
        # This is a mock implementation
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.exportduties.com/v1/rates"
            headers = {"Authorization": f"Bearer {self.export_duty_api_key}"}
            params = {
                "materials": ",".join(materials),
                "country": origin_country
            }
            
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {material: rate for material, rate in data["duty_rates"].items()}
                    else:
                        # Fallback to mock data if API fails
                        print(f"Warning: Export duty API returned status {response.status}. Using mock data.")
            except Exception as e:
                print(f"Error fetching export duties: {str(e)}. Using mock data.")
        
        # Mock data as fallback (percentage rates)
        return {
            "Plastic": 2.0,
            "Glass": 1.5,
            "Cardboard": 0.5,
            "Aluminum": 3.0,
            "Paper": 0.0,
            "Biodegradable Plastic": 0.0,
            "Steel": 2.5,
            "Wood": 1.0,
            "Cork": 0.5,
            "Fabric": 1.5
        }

    def _get_timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _save_report_to_file(self, data: Dict[str, Any], filename_prefix: str) -> str:
        filename = f"{filename_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    async def calculate_total_cost_per_kg(
        self, 
        materials: List[str], 
        origin_country: str = "CN", 
        destination_country: str = "US", 
        weight_kg: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate the total cost per kg for each material including production cost, tariffs, and export duties.
        
        Args:
            materials: List of material names
            origin_country: Country code where materials are produced
            destination_country: Country code where materials are imported
            weight_kg: Weight in kilograms for cost calculation base
            
        Returns:
            Dictionary with cost analysis
        """
        try:
            # Fetch all required data concurrently
            production_costs_task = self.fetch_production_costs(materials, origin_country)
            tariffs_task = self.fetch_tariffs(materials, origin_country, destination_country)
            export_duties_task = self.fetch_export_duties(materials, origin_country)
            
            production_costs, tariffs, export_duties = await asyncio.gather(
                production_costs_task, tariffs_task, export_duties_task
            )
            
            # Prepare data for the AI agent to analyze
            materials_data = []
            for material in materials:
                if material in production_costs and material in tariffs and material in export_duties:
                    materials_data.append({
                        "material_name": material,
                        "production_cost_per_kg": production_costs[material],
                        "tariff_rate_percent": tariffs[material],
                        "export_duty_percent": export_duties[material]
                    })
            
            # Use the AI agent to analyze the costs and generate insights
            prompt = f"""
You are a packaging material cost analysis AI. Analyze the following materials data and calculate the total cost per kg.

MATERIALS DATA:
{json.dumps(materials_data, indent=2)}

TASK:
1. Calculate the total cost per kg for each material using this formula:
   Total Cost = Production Cost + (Production Cost × Tariff Rate/100) + (Production Cost × Export Duty/100)

2. Rank the materials from most economical to least economical.

3. Provide specific insights about each material's cost factors and trade considerations.

RESPONSE FORMAT (STRICT JSON):
{{
  "cost_analysis": [
    {{
      "material_name": "[material name]",
      "production_cost_per_kg": [numeric value],
      "tariff_cost_per_kg": [numeric value],
      "export_duty_cost_per_kg": [numeric value],
      "total_cost_per_kg": [numeric value],
      "cost_breakdown_percentage": {{
        "production": [percent value],
        "tariff": [percent value],
        "export_duty": [percent value]
      }},
      "insights": "[specific insights about this material's costs]"
    }}
    // Repeat for each material
  ],
  "rankings": {{
    "most_economical": ["[material1]", "[material2]", "[material3]"],
    "least_economical": ["[materialX]", "[materialY]", "[materialZ]"]
  }},
  "summary": {{
    "average_total_cost": [numeric value],
    "tariff_impact_analysis": "[analysis of how tariffs affect overall costs]",
    "export_duty_impact_analysis": "[analysis of how export duties affect overall costs]",
    "recommendations": [
      "[recommendation 1]",
      "[recommendation 2]",
      "[recommendation 3]"
    ]
  }}
}}

INSTRUCTIONS:
- Respond with VALID JSON only
- Calculate all costs based on 1 kg of material
- Round all numeric values to 2 decimal places
- Ensure cost breakdowns add up to 100%
- Provide substantive, specific insights for each material
- Do not add any materials not in the original list
"""

            response = await self.agent.arun(prompt)
            response_text = response.content.strip()
            
            # Clean up response to ensure it's valid JSON
            for tag in ["```json", "```"]:
                if response_text.startswith(tag): 
                    response_text = response_text[len(tag):]
                if response_text.endswith(tag): 
                    response_text = response_text[:-len(tag)]
            
            analysis = json.loads(response_text.strip())
            
            # Add metadata to the analysis
            result = {
                "materials_cost_analysis": analysis,
                "analysis_parameters": {
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "weight_kg_base": weight_kg,
                    "analysis_timestamp": self._get_timestamp(),
                    "user_login": self.user_login
                }
            }
            
            # Save the results to a file
            report_path = self._save_report_to_file(result, f"packaging_cost_analysis_{origin_country}_to_{destination_country}")
            result["report_path"] = report_path
            
            return result
            
        except Exception as e:
            error = {
                "error": f"Packaging material cost analysis failed: {str(e)}",
                "materials": materials,
                "timestamp": self._get_timestamp(),
                "user_login": self.user_login
            }
            error_path = self._save_report_to_file(error, "error_packaging_cost_analysis")
            error["report_path"] = error_path
            return error

    async def generate_cost_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable report from the cost analysis."""
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"
        
        cost_analysis = analysis["materials_cost_analysis"]["cost_analysis"]
        rankings = analysis["materials_cost_analysis"]["rankings"]
        summary = analysis["materials_cost_analysis"]["summary"]
        params = analysis["analysis_parameters"]
        
        report = f"""
Packaging Material Cost Analysis Report
======================================
Date: {params['analysis_timestamp']}
Origin Country: {params['origin_country']}
Destination Country: {params['destination_country']}
Generated by: {params['user_login']}

Cost Summary
-----------
Average Total Cost: ${summary['average_total_cost']}/kg

Most Economical Materials:
{', '.join(rankings['most_economical'])}

Least Economical Materials:
{', '.join(rankings['least_economical'])}

Detailed Material Analysis
------------------------
"""
        
        # Sort materials by total cost (ascending)
        sorted_materials = sorted(cost_analysis, key=lambda x: x['total_cost_per_kg'])
        
        for material in sorted_materials:
            report += f"\n{material['material_name']}:\n"
            report += f"  Total Cost: ${material['total_cost_per_kg']}/kg\n"
            report += f"  - Production: ${material['production_cost_per_kg']}/kg ({material['cost_breakdown_percentage']['production']}%)\n"
            report += f"  - Tariff: ${material['tariff_cost_per_kg']}/kg ({material['cost_breakdown_percentage']['tariff']}%)\n"
            report += f"  - Export Duty: ${material['export_duty_cost_per_kg']}/kg ({material['cost_breakdown_percentage']['export_duty']}%)\n"
            report += f"  Insights: {material['insights']}\n"
        
        report += f"\nTariff Impact: {summary['tariff_impact_analysis']}\n"
        report += f"\nExport Duty Impact: {summary['export_duty_impact_analysis']}\n"
        
        report += "\nRecommendations:\n"
        for i, rec in enumerate(summary['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        report += f"\nFull report saved to: {analysis['report_path']}"
        
        return report

# --- Script Entry Point ---
async def main():
    try:
        agent = PackagingCostAgent()
        
        # List of materials to analyze
        materials = [
            "Plastic", "Glass", "Cardboard", "Aluminum", 
            "Paper", "Biodegradable Plastic", "Steel"
        ]
        
        # Parameters for analysis
        origin_country = "CN"  # China
        destination_country = "US"  # United States
        
        print(f"Analyzing packaging material costs from {origin_country} to {destination_country}...")
        analysis = await agent.calculate_total_cost_per_kg(
            materials=materials,
            origin_country=origin_country,
            destination_country=destination_country
        )
        
        report = await agent.generate_cost_report(analysis)
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())