from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Import all agents
from MaterialDB_agent import PackagingMaterialsAgent
from Product_Analyst import ProductCompatibilityAgent
from Material_Analyst import MaterialPropertiesAgent
from Logistics_Analyst import LogisticCompatibilityAgent
from Sourcing_Cost_Analyser import ProductionCostAgent
from Sustainability_Analyst import EnvironmentalImpactAgent
from Consumer_Behaviour_Analyst import ConsumerBehaviorAgent

class MaterialSelectionEngine:
    """Handles final material selection with weighted analysis and reasoning."""
    
    def __init__(self):
        self.weights = {
            "material_properties": 0.20,
            "logistics": 0.15,
            "cost": 0.25,
            "sustainability": 0.20,
            "consumer": 0.20
        }

    def evaluate_material(self, material_name: str, scores: Dict[str, float]) -> Dict[str, Any]:
        """Evaluates a single material across all criteria."""
        strengths = []
        weaknesses = []
        weighted_score = 0

        for criterion, weight in self.weights.items():
            score = scores.get(criterion, 0)
            weighted_score += score * weight
            
            if score >= 8:
                strengths.append(f"Excellent {criterion.replace('_', ' ')} ({score:.1f}/10)")
            elif score >= 7:
                strengths.append(f"Strong {criterion.replace('_', ' ')} ({score:.1f}/10)")
            elif score <= 4:
                weaknesses.append(f"Poor {criterion.replace('_', ' ')} ({score:.1f}/10)")

        return {
            "material_name": material_name,
            "overall_score": weighted_score,
            "component_scores": scores,
            "strengths": strengths[:3],  # Top 3 strengths
            "weaknesses": weaknesses[:2],  # Top 2 weaknesses
            "reasoning": self._generate_reasoning(material_name, weighted_score, strengths, weaknesses)
        }

    def _generate_reasoning(self, material: str, score: float, strengths: List[str], weaknesses: List[str]) -> str:
        """Generates detailed reasoning for material selection."""
        reasoning = [f"{material} achieved an overall score of {score:.2f}/10."]
        
        if strengths:
            reasoning.append("Key strengths include: " + "; ".join(strengths))
        
        if weaknesses:
            reasoning.append("Consider these limitations: " + "; ".join(weaknesses))
        
        if score >= 8:
            reasoning.append("Highly recommended for this application.")
        elif score >= 7:
            reasoning.append("Recommended with minor considerations.")
        elif score >= 5:
            reasoning.append("Suitable with some limitations.")
        else:
            reasoning.append("May require alternatives or modifications.")
            
        return " ".join(reasoning)

class PackagingOrchestrator:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Directory setup
        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        # Fixed metadata
        self.user_login = "codegeek03"
        self.current_time = "2025-04-19 22:11:27"

        # Initialize agents and selection engine
        self.agents = {
            "material_db": PackagingMaterialsAgent(model_id, enable_markdown),
            "product": ProductCompatibilityAgent(model_id, enable_markdown),
            "material": MaterialPropertiesAgent(model_id, enable_markdown),
            "logistics": LogisticCompatibilityAgent(model_id, enable_markdown),
            "cost": ProductionCostAgent(model_id, enable_markdown),
            "sustainability": EnvironmentalImpactAgent(model_id, enable_markdown),
            "consumer": ConsumerBehaviorAgent(model_id, enable_markdown)
        }
        self.selection_engine = MaterialSelectionEngine()

    async def run_concurrent_analyses(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs all analyses concurrently."""
        analysis_tasks = {
            "material": self.agents["material"].analyze_material_properties(material_data),
            "logistics": self.agents["logistics"].analyze_logistics_compatibility(material_data),
            "cost": self.agents["cost"].analyze_production_costs(material_data),
            "sustainability": self.agents["sustainability"].analyze_environmental_impact(material_data),
            "consumer": self.agents["consumer"].analyze_consumer_behavior(material_data)
        }

        results = await asyncio.gather(*analysis_tasks.values(), return_exceptions=True)
        return dict(zip(analysis_tasks.keys(), results))

    async def analyze_materials(self, product_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrates the complete analysis process with error handling."""
        try:
            analyses = {}
            
            # Sequential: Product Analysis & Material DB Search
            print("\n1. Analyzing product requirements...")
            analyses["product"] = await self.agents["product"].analyze_product_compatibility(product_requirements)

            print("\n2. Searching material database...")
            material_data = await self.agents["material_db"].analyze_packaging_materials(product_requirements["product_name"])

            # Parallel: Run all other analyses
            print("\n3. Running concurrent analyses...")
            parallel_analyses = await self.run_concurrent_analyses(material_data)
            analyses.update(parallel_analyses)

            # Error checking
            errors = {k: str(v) for k, v in analyses.items() if isinstance(v, Exception)}
            if errors:
                raise ValueError(f"Analysis errors encountered: {json.dumps(errors, indent=2)}")

            # Generate recommendations
            print("\n4. Generating final recommendations...")
            recommendations = await self._generate_recommendations(analyses)

            final_analysis = {
                "product_name": product_requirements["product_name"],
                "timestamp": self.current_time,
                "user": self.user_login,
                "analyses": analyses,
                "recommendations": recommendations
            }

            # Save report
            final_analysis["report_path"] = self._save_report(final_analysis)
            return final_analysis

        except Exception as e:
            return self._handle_error(str(e))

    async def _generate_recommendations(self, analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates final recommendations using the selection engine."""
        all_materials = set()
        scores_by_material = {}

        # Collect scores from all analyses
        for analysis_type, analysis in analyses.items():
            if analysis_type not in ["product", "material_db"] and "top_materials" in analysis:
                for material in analysis["top_materials"]:
                    name = material["material_name"]
                    all_materials.add(name)
                    if name not in scores_by_material:
                        scores_by_material[name] = {}
                    scores_by_material[name][analysis_type] = material.get("overall_score", 0)

        # Evaluate each material
        evaluations = [
            self.selection_engine.evaluate_material(material, scores)
            for material, scores in scores_by_material.items()
        ]

        # Return top 5 recommendations
        return sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)[:5]

    def _save_report(self, data: Dict[str, Any]) -> str:
        """Saves the analysis report to file."""
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"packaging_analysis_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Creates a standardized error report."""
        error_data = {
            "error": f"Analysis failed: {error_message}",
            "timestamp": self.current_time,
            "user": self.user_login
        }
        error_data["report_path"] = self._save_report(error_data)
        return error_data

    async def generate_final_report(self, analysis: Dict[str, Any]) -> str:
        """Generates a comprehensive final report with detailed analysis."""
        if "error" in analysis:
            return f"Error in analysis: {analysis['error']}"

        report = f"""
Packaging Material Analysis Report
================================
Product: {analysis['product_name']}
Analysis Date: {analysis['timestamp']}
Generated by: {analysis['user']}

Executive Summary
----------------
A comprehensive analysis was performed across multiple criteria including material properties,
logistics compatibility, production costs, environmental impact, and consumer preferences.

Top Recommended Materials
-----------------------"""

        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"\n\n{i}. {rec['material_name']}"
            report += f"\nOverall Score: {rec['overall_score']:.2f}/10"
            
            if rec['strengths']:
                report += "\nKey Strengths:"
                for strength in rec['strengths']:
                    report += f"\n  • {strength}"
            
            if rec['weaknesses']:
                report += "\nConsiderations:"
                for weakness in rec['weaknesses']:
                    report += f"\n  • {weakness}"
            
            report += f"\nDetailed Assessment:"
            for component, score in rec['component_scores'].items():
                report += f"\n  • {component.replace('_', ' ').title()}: {score:.1f}/10"
            
            report += f"\n\nReasoning:\n{rec['reasoning']}"

        report += "\n\nAnalysis Details by Component\n" + "=" * 30

        # Add component-wise analysis summaries
        for component, analysis_data in analysis['analyses'].items():
            if component not in ["product", "material_db"]:
                report += f"\n\n{component.title()} Analysis:"
                report += "\n" + "-" * (len(component) + 9)
                
                if isinstance(analysis_data, dict):
                    if "summary" in analysis_data:
                        for key, value in analysis_data["summary"].items():
                            report += f"\n• {key.replace('_', ' ').title()}: {value}"
                    elif "top_materials" in analysis_data:
                        report += "\nTop Performers:"
                        for mat in analysis_data["top_materials"][:3]:
                            report += f"\n• {mat['material_name']}"
                            if "overall_score" in mat:
                                report += f" (Score: {mat['overall_score']:.1f}/10)"

        # Add analysis metrics
        report += "\n\nAnalysis Metrics"
        report += "\n" + "=" * 15
        report += f"\n• Total materials analyzed: {len(analysis['analyses'].get('material_db', {}).get('materials', []))}"
        report += f"\n• Analysis components: {len(analysis['analyses']) - 2}"
        report += f"\n• Top recommendations provided: {len(analysis['recommendations'])}"
        report += f"\n• Analysis timestamp: {analysis['timestamp']}"
        
        return report

async def main():
    try:
        # Example product requirements
        product_requirements = {
            "product_name": "Eco-Friendly Bottle",
            "product_type": "Beverage Container",
            "capacity": "500ml",
            "target_market": "Environmentally conscious consumers",
            "special_requirements": {
                "recyclable": True,
                "food_safe": True,
                "temperature_resistant": True,
                "shelf_life": "12 months",
                "uv_resistant": True
            },
            "industry_standards": [
                "FDA Food Contact",
                "ISO 14001",
                "BPA Free"
            ],
            "market_details": {
                "primary_region": "North America",
                "price_segment": "Premium",
                "distribution_channels": ["Retail", "E-commerce"],
                "batch_size": "100000 units"
            }
        }

        orchestrator = PackagingOrchestrator()
        
        print("\nInitiating Comprehensive Packaging Analysis")
        print("=" * 45)
        print(f"Product: {product_requirements['product_name']}")
        print(f"Time: {orchestrator.current_time}")
        print(f"User: {orchestrator.user_login}")
        print("=" * 45)

        # Run analysis
        analysis = await orchestrator.analyze_materials(product_requirements)
        
        if "error" in analysis:
            print(f"\nAnalysis Error: {analysis['error']}")
            return

        # Generate and display report
        report = await orchestrator.generate_final_report(analysis)
        print("\nPackaging Analysis Report")
        print("=" * 45)
        print(report)
        
        # Save information
        print(f"\nDetailed analysis saved to: {analysis['report_path']}")
        
        # Additional result metrics
        print("\nAnalysis Metrics:")
        print(f"• Total materials analyzed: {len(analysis['analyses'].get('material_db', {}).get('materials', []))}")
        print(f"• Analysis components: {len(analysis['analyses']) - 2}")
        print(f"• Top recommendations provided: {len(analysis['recommendations'])}")

    except Exception as e:
        print("\nFatal Error in Analysis Process")
        print("=" * 45)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {str(e)}")
        print("\nPlease check the input requirements and try again.")

if __name__ == "__main__":
    asyncio.run(main())