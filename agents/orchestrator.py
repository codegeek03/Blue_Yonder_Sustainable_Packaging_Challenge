from typing import Dict, Any, List
import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import shutil

# Import the agents
from Environment_impact_agent import EnvironmentalImpactAgent
from logistics import LogisticsCostAnalyzerAgent
from Material_cost_analyser import MaterialCostAgent
from Material_property_analyser import MaterialPropertiesAgent
from MaterialDB_agent import PackagingMaterialsAgent
from product_compatibilty import ProductCompatibilityAgent

class PackagingAnalysisOrchestrator:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        # Create output directories
        self.output_dir = "analysis_reports"
        self.material_reports_dir = "material_reports"
        self.temp_kb_dir = "temp_KB"  # Add temp_KB directory reference
        
        # Create directories if they don't exist
        for directory in [self.output_dir, self.material_reports_dir]:
            os.makedirs(directory, exist_ok=True)

        # Initialize MaterialDB agent first
        self.material_db_agent = PackagingMaterialsAgent(model_id, enable_markdown)
        
        # Initialize other agents
        self.agents = {
            "environmental": EnvironmentalImpactAgent(model_id, enable_markdown),
            "logistics": LogisticsCostAnalyzerAgent(model_id, enable_markdown),
            "cost": MaterialCostAgent(model_id, enable_markdown),
            "properties": MaterialPropertiesAgent(model_id, enable_markdown),
            "compatibility": ProductCompatibilityAgent(model_id, enable_markdown)
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in YYYY-MM-DD HH:MM:SS format."""
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _move_material_report(self, product_name: str) -> bool:
        """
        Move material report from temp_KB to material_reports directory.

        Args:
            product_name: Name of the product

        Returns:
            bool: True if move was successful, False otherwise
        """
        temp_filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        temp_filepath = os.path.join(self.temp_kb_dir, temp_filename)
        target_filepath = os.path.join(self.material_reports_dir, temp_filename)

        if os.path.exists(temp_filepath):
            shutil.copy2(temp_filepath, target_filepath)
            return True
        return False

    def _check_material_report(self, product_name: str) -> Dict[str, Any]:
        """
        Check and load material report from either temp_KB or material_reports.

        Args:
            product_name: Name of the product

        Returns:
            Dict containing the material report data
        """
        filename = f"{product_name.replace(' ', '_')}_materials_report.json"
        temp_filepath = os.path.join(self.temp_kb_dir, filename)
        target_filepath = os.path.join(self.material_reports_dir, filename)

        # First check temp_KB
        if os.path.exists(temp_filepath):
            with open(temp_filepath, 'r') as f:
                report = json.load(f)
            # Move to material_reports directory
            self._move_material_report(product_name)
            return report
        
        # Then check material_reports
        if os.path.exists(target_filepath):
            with open(target_filepath, 'r') as f:
                return json.load(f)
                
        return {"error": "Material report not found"}

    def _save_consolidated_report(self, data: Dict[str, Any], product_name: str) -> str:
        filename = f"{product_name.replace(' ', '_')}_consolidated_report.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filepath

    async def run_analysis_workflow(self, product_name: str) -> Dict[str, Any]:
        try:
            print(f"\nStarting comprehensive analysis for: {product_name}")
            print("=" * 50)

            # Step 1: Check for existing material report
            print("\n1. Checking for material analysis...")
            materials_analysis = self._check_material_report(product_name)

            if "error" in materials_analysis:
                print("Material report not found. Generating new material analysis...")
                materials_analysis = await self.material_db_agent.analyze_packaging_materials(product_name)
                if "error" in materials_analysis:
                    raise ValueError(f"Materials analysis failed: {materials_analysis['error']}")
            else:
                print("Using existing material analysis...")

            print(f"Material analysis complete. Found {len(materials_analysis['materials'])} materials.")

            # Initialize analyses dictionary
            analyses = {"materials": materials_analysis}

            # Run subsequent analyses
            for step, (name, agent) in enumerate([
                ("environmental", self.agents["environmental"]),
                ("logistics", self.agents["logistics"]),
                ("cost", self.agents["cost"]),
                ("properties", self.agents["properties"]),
                ("compatibility", self.agents["compatibility"])
            ], 2):
                print(f"\n{step}. Analyzing {name}...")
                analyses[name] = await getattr(agent, f"analyze_{name}_{'impact' if name == 'environmental' else 'costs' if name in ['logistics', 'cost'] else 'properties' if name == 'properties' else 'product'}")(product_name)

            # Consolidate report
            consolidated_report = {
                "product_name": product_name,
                "analysis_timestamp": self._get_timestamp(),
                "analyses": analyses
            }

            # Save consolidated report
            report_path = self._save_consolidated_report(consolidated_report, product_name)
            print(f"\nAnalysis complete. Consolidated report saved to: {report_path}")

            return consolidated_report

        except Exception as e:
            error_report = {
                "error": f"Analysis workflow failed: {str(e)}",
                "product_name": product_name,
                "timestamp": self._get_timestamp()
            }
            self._save_consolidated_report(error_report, f"error_{product_name}")
            return error_report

    async def generate_summary_report(self, consolidated_report: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of all analyses.

        Args:
            consolidated_report: The consolidated analysis results

        Returns:
            Formatted summary report as a string
        """
        if "error" in consolidated_report:
            return f"Error in analysis: {consolidated_report['error']}"

        summary = f"""
Comprehensive Packaging Analysis Report
=====================================
Product: {consolidated_report['product_name']}
Analysis Date: {consolidated_report['analysis_timestamp']}

1. Material Options
------------------
Total materials analyzed: {len(consolidated_report['analyses']['materials']['materials'])}
Top materials identified:
"""
        # Add top 5 materials
        for i, material in enumerate(consolidated_report['analyses']['materials']['materials'][:5], 1):
            summary += f"  {i}. {material['material_name']}\n     Justification: {material['justification']}\n"

        # Add environmental impact summary
        env_analysis = consolidated_report['analyses']['environmental']
        if 'materials_analysis' in env_analysis:
            env_summary = env_analysis['materials_analysis'][0]
            summary += f"""
2. Environmental Impact
---------------------
Top environmental performers:
"""
            for mat in env_analysis.get('summary', {}).get('best_performers', [])[:3]:
                summary += f"- {mat}\n"

        # Add logistics summary
        logistics = consolidated_report['analyses']['logistics']
        if 'logistics_analysis' in logistics:
            summary += f"""
3. Logistics Analysis
-------------------
Key logistics metrics:
"""
            for metric, data in logistics['logistics_analysis'][0]['metrics'].items():
                summary += f"- {metric.replace('_', ' ').title()}: {data['details']}\n"

        # Add cost analysis summary
        cost = consolidated_report['analyses']['cost']
        summary += f"""
4. Cost Analysis
--------------
Most economical materials:
"""
        for mat in cost.get('summary', {}).get('most_economical_materials', [])[:3]:
            summary += f"- {mat}\n"

        # Add properties summary
        props = consolidated_report['analyses']['properties']
        if 'summary' in props and 'by_property' in props['summary']:
            summary += f"""
5. Material Properties
-------------------
Top performing materials by property:
"""
            for prop, materials in props['summary']['by_property'].items():
                summary += f"- {prop.replace('_', ' ').title()}: {', '.join(materials[:2])}\n"

        # Add compatibility summary
        compat = consolidated_report['analyses']['compatibility']
        summary += f"""
6. Product Compatibility
---------------------
Overall compatibility score: {compat.get('overall_score', 'N/A')}/10
"""

        return summary

async def main():
    try:
        # Create orchestrator instance
        orchestrator = PackagingAnalysisOrchestrator()

        # Example product to analyze
        product_name = "Glass Bottle"

        # Run complete analysis
        print("Starting comprehensive packaging analysis...")
        consolidated_results = await orchestrator.run_analysis_workflow(product_name)

        # Generate and print summary report
        summary_report = await orchestrator.generate_summary_report(consolidated_results)
        print("\nSummary Report:")
        print(summary_report)

    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())