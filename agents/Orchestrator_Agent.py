from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime

class OrchestrationAgent:
    def __init__(self, current_time: str = "2025-05-09 18:11:02", current_user: str = "codegeek03"):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.current_time = current_time
        self.user_login = current_user

        # Initialize Gemini agent
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
            markdown=True
        )

        self.analysis_weights = ANALYSIS_WEIGHTS

    async def generate_material_analysis(self, material: Dict[str, Any], dimension_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analysis for a single material"""
        prompt = f"""
Analyze this material's performance across all dimensions:

Material: {material.get('material_name', material.get('id', material.get('name', 'Unknown')))}
Overall Score: {material.get('total_score', 0)}

Dimensional Scores:
{json.dumps(dimension_scores, indent=2)}

Provide analysis in this JSON format:
{{
    "dimensional_analysis": {{
        "properties": {{
            "strengths": [<list of key strengths>],
            "limitations": [<list of limitations>],
            "improvement_areas": [<list of potential improvements>]
        }},
        "logistics": {{
            "advantages": [<list of advantages>],
            "challenges": [<list of challenges>],
            "optimization_opportunities": [<list of opportunities>]
        }},
        "cost": {{
            "benefits": [<list of cost benefits>],
            "concerns": [<list of cost concerns>],
            "efficiency_suggestions": [<list of suggestions>]
        }},
        "sustainability": {{
            "positives": [<list of environmental benefits>],
            "negatives": [<list of environmental concerns>],
            "mitigation_strategies": [<list of strategies>]
        }},
        "consumer": {{
            "advantages": [<list of market advantages>],
            "considerations": [<list of market considerations>],
            "market_opportunities": [<list of opportunities>]
        }}
    }},
    "competitive_analysis": {{
        "unique_selling_points": [<list of USPs>],
        "market_positioning": "<positioning statement>",
        "target_applications": [<list of ideal applications>]
    }},
    "risk_assessment": {{
        "technical_risks": [<list of risks>],
        "market_risks": [<list of risks>],
        "mitigation_strategies": [<list of strategies>]
    }}
}}

Keep responses concise (under 100 characters per item) and focus on actionable insights.
"""
        try:
            response = await self.agent.arun(prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Material analysis generation failed: {e}")
            return {"error": str(e)}

    async def generate_comparative_analysis(self, top_materials: List[Dict[str, Any]], avg_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate comparative analysis between top materials"""
        prompt = f"""
Analyze the comparative performance of top materials:

Top Materials:
{json.dumps([{
    'name': m.get('material_name', m.get('id', m.get('name', 'Unknown'))),
    'score': m.get('total_score', 0),
    'scores': m.get('reasoning', {}).get('score_breakdown', {})
} for m in top_materials], indent=2)}

Average Scores:
{json.dumps(avg_scores, indent=2)}

Provide analysis in this JSON format:
{{
    "performance_patterns": [
        {{
            "pattern": "<observed pattern>",
            "significance": "<business impact>",
            "affected_materials": ["<material names>"]
        }}
    ],
    "comparative_advantages": [
        {{
            "material": "<name>",
            "advantages": ["<list of advantages>"],
            "best_use_cases": ["<list of applications>"]
        }}
    ],
    "trade_offs": [
        {{
            "description": "<trade-off description>",
            "affected_dimensions": ["<dimensions>"],
            "optimization_suggestions": ["<suggestions>"]
        }}
    ],
    "market_implications": {{
        "opportunities": ["<list of opportunities>"],
        "challenges": ["<list of challenges>"],
        "recommendations": ["<list of recommendations>"]
    }}
}}

Keep each text entry under 100 characters and focus on actionable insights.
"""
        try:
            response = await self.agent.arun(prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Comparative analysis generation failed: {e}")
            return {"error": str(e)}

    async def generate_executive_summary(self, final_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of the analysis"""
        prompt = f"""
Generate executive summary for material selection analysis:

Product: {final_results['product_name']}
Total Materials Analyzed: {final_results['analysis_summary']['total_materials_analyzed']}
Score Distribution: {json.dumps(final_results['analysis_summary']['score_distribution'], indent=2)}
Top Performers: {json.dumps([{
    'name': m.get('material_name', m.get('id', m.get('name', 'Unknown'))),
    'score': m.get('total_score', 0)
} for m in final_results['top_materials'][:3]], indent=2)}

Provide summary in this JSON format:
{{
    "executive_summary": {{
        "key_findings": [
            {{
                "finding": "<observation>",
                "business_impact": "<impact>",
                "confidence": "high|medium|low"
            }}
        ],
        "recommendations": [
            {{
                "action": "<recommendation>",
                "priority": "high|medium|low",
                "rationale": "<reason>"
            }}
        ],
        "strategic_implications": {{
            "short_term": ["<implications>"],
            "medium_term": ["<implications>"],
            "long_term": ["<implications>"]
        }},
        "risk_assessment": {{
            "primary_risks": ["<risks>"],
            "mitigation_strategies": ["<strategies>"]
        }}
    }}
}}

Keep each text entry under 100 characters and focus on actionable insights.
"""
        try:
            response = await self.agent.arun(prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {"error": str(e)}

    def _save_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Save report to file"""
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return filepath