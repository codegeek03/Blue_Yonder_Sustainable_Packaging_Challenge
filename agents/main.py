from typing import Dict, Any, List, Literal, TypedDict, Annotated, Optional, NotRequired, Union
from datetime import datetime, timezone
import logging
import os
import json
import asyncio
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# Agno imports
from agno.agent import Agent
from agno.models.google import Gemini

# Constants
CURRENT_USER = "codegeek03"
CURRENT_TIME = "2025-05-09 21:01:46"  # Updated with provided time

ANALYSIS_WEIGHTS = {
    "properties": 1.0,
    "logistics": 0.8,
    "cost": 1.2,
    "sustainability": 1.0,
    "consumer": 1.5
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# State definition
class AnalysisState(TypedDict):
    input_data: Annotated[Dict[str, Any], "input_data"]
    compatibility_analysis: Annotated[Dict[str, Any], "compatibility_analysis"]
    material_database: Annotated[Dict[str, Any], "material_database"]
    properties_analysis: Annotated[Dict[str, Any], "properties_analysis"]
    logistics_analysis: Annotated[Dict[str, Any], "logistics_analysis"]
    cost_analysis: Annotated[Dict[str, Any], "cost_analysis"]
    sustainability_analysis: Annotated[Dict[str, Any], "sustainability_analysis"]
    consumer_analysis: Annotated[Dict[str, Any], "consumer_analysis"]
    final_results: Annotated[Dict[str, Any], "final_results"]
    input_status: Annotated[str, "input_status"]
    compatibility_status: Annotated[str, "compatibility_status"]
    material_db_status: Annotated[str, "material_db_status"]
    properties_status: Annotated[str, "properties_status"]
    logistics_status: Annotated[str, "logistics_status"]
    costs_status: Annotated[str, "costs_status"]
    sustainability_status: Annotated[str, "sustainability_status"]
    consumer_status: Annotated[str, "consumer_status"]
    orchestration_status: Annotated[str, "orchestration_status"]
    error: Annotated[Optional[str], "error"]
    user_login: Annotated[str, "user_login"]
    current_time: Annotated[str, "current_time"]

class OrchestrationAgent:
    """
    An agent that orchestrates the material analysis process and generates
    comprehensive reports using Gemini for enhanced analysis.
    """
    
    def __init__(self, current_time: str = CURRENT_TIME, current_user: str = CURRENT_USER):
        logger.info("Initializing OrchestrationAgent")
        try:
            self.current_time = current_time
            self.user_login = current_user
            
            # Load environment variables
            load_dotenv()
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is not set")

            # Create reports directory
            self.reports_dir = "temp_KB/reports"
            os.makedirs(self.reports_dir, exist_ok=True)

            # Initialize Gemini agent
            self.agent = Agent(
                model=Gemini(
                    id="gemini-2.0-flash-exp",
                    api_key=self.api_key
                ),
                markdown=True,
            )

            # Analysis weights
            self.analysis_weights = ANALYSIS_WEIGHTS.copy()
            
            logger.info("OrchestrationAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize OrchestrationAgent: {str(e)}", exc_info=True)
            raise

    async def generate_executive_summary(
    self,
    product_name: str,
    k: int,
    material: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analysis for a single material."""
        try:
            prompt = f"""
You are a senior sustainability consultant for Blue Yonder’s “Data Analytics Driven Framework for Sustainable Packaging Decisions” challenge. You’ve been given:

• Product: {product_name}  
• One of the top-{k} packaging materials from a data-driven ranking: **{material['material_name']}**  
• A holistic view of this material’s performance across five dimensions:  
  – Properties  
  – Logistics  
  – Cost  
  – Sustainability  
  – Consumer Preference  

Blue Yonder requires a professional, slide-ready report for each material, covering:

1. **Executive Snapshot**  
   – A one-sentence verdict on this material’s suitability for packaging **{product_name}**.

2. **Composite Score**  
   – A single “Sustainability Impact Score” (0–100) computed by weighting each dimension (Properties 6, Logistics 5, Cost 6, Sustainability 9, Consumer 7).  
   – Only the final composite (no raw sub-scores).

3. **Strengths & Alignment**  
   – 2–3 key strengths, tied explicitly to Blue Yonder’s priorities (e.g. Sustainability, Consumer Preference).

4. **Trade-off Analysis**  
   – Any weaker dimensions and how higher-priority strengths compensate.

5. **Supply-Chain Implications**  
   – Direct/indirect cost impacts (handling, logistics, damage risk), regulatory fit, and consumer acceptance.

6. **Strategic Recommendation**  
   – Data-grounded “Adopt” (true/false) recommendation for packaging **{product_name}**, including:  
     • Estimated % improvement in overall sustainability footprint  
     • Estimated % change in cost  
     • Any regulatory or consumer considerations  

**Return exactly this JSON** (no extra keys or prose):

```json
{{
  "material_name": "{material['material_name']}",
  "executive_snapshot": "<one-sentence verdict>",
  "composite_score": <0–100>,
  "strengths": [
    {{
      "dimension": "<name>",
      "insight": "<why this is a strength & business impact>"
    }}
  ],
  "trade_offs": [
    {{
      "dimension": "<weaker area>",
      "mitigation": "<how higher-priority strengths offset it>"
    }}
  ],
  "supply_chain_implications": {{
    "costs": "<direct/indirect cost narrative>",
    "logistics": "<handling & transport narrative>",
    "regulatory": "<regulatory fit overview>",
    "consumer": "<consumer acceptance outlook>"
  }},
  "recommendation": {{
    "adopt": <true|false>,
    "justification": "<data-driven rationale>",
    "sustainability_gain_percent": <estimated %>,
    "cost_delta_percent": <estimated %>
  }}
}}"""

            response = await self.agent.arun(prompt)
            return self._process_response(response.content)

        except Exception as e:
            logger.error(f"Error analysis failed: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _process_response(self, response_text: str) -> Dict[str, Any]:
        """Process and clean up the response text."""
        try:
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response JSON: {str(e)}")
            raise ValueError(f"Invalid JSON response: {str(e)}")

    def _save_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Save report to file."""
        try:
            timestamp = self.current_time.replace(" ", "_").replace(":", "-")
            filename = f"{report_type}_{timestamp}.json"
            filepath = os.path.join(self.reports_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {report_type} report to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}", exc_info=True)
            raise

# Import all your agents
from detail_input import ProductInput
from Product_Analyst import ProductCompatibilityAgent
from MaterialDB_agent import PackagingMaterialsAgent
from Material_Analyst import MaterialPropertiesAgent
from Logistics_Analyst import LogisticCompatibilityAgent
from Sourcing_Cost_Analyser import ProductionCostAgent
from Sustainability_Analyst import EnvironmentalImpactAgent
from Consumer_Behaviour_Analyst import ConsumerBehaviorAgent

# Node definitions
async def process_input(state: AnalysisState) -> Dict:
    logger.info("Starting input processing")
    try:
        if not state.get("input_data"):
            agent = ProductInput(CURRENT_TIME, CURRENT_USER)
            details = await agent.get_product_details()
            
            return {
                "input_data": details,
                "input_status": "completed",
                "user_login": CURRENT_USER,
                "current_time": CURRENT_TIME
            }
        return {}
    except Exception as e:
        msg = f"Input processing failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "input_status": "failed"
        }

async def analyze_product_compatibility(state: AnalysisState) -> Dict:
    logger.info("Starting product compatibility analysis")
    try:
        if state.get("error"): return {}
        agent = ProductCompatibilityAgent()
        result = await agent.analyze_product_compatibility(
            state["input_data"]["product_name"], 
            state["input_data"]
        )
        return {
            "compatibility_analysis": result,
            "compatibility_status": "completed"
        }
    except Exception as e:
        msg = f"Product compatibility analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "compatibility_status": "failed"
        }

async def query_material_database(state: AnalysisState) -> Dict:
    logger.info("Starting material database query")
    try:
        if state.get("error"): return {}
        agent = PackagingMaterialsAgent(CURRENT_USER, CURRENT_TIME)
        result = await agent.find_materials_by_criteria(state["compatibility_analysis"])
        if not result.get("materials"):
            raise ValueError("No compatible materials found")
        return {
            "material_database": result,
            "material_db_status": "completed"
        }
    except Exception as e:
        msg = f"Material DB query failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "material_db_status": "failed"
        }

async def analyze_material_properties(state: AnalysisState) -> Dict:
    logger.info("Starting material properties analysis")
    if state.get("error"): return {}
    try:
        agent = MaterialPropertiesAgent()
        result = await agent.analyze_material_properties(state["material_database"])
        return {
            "properties_analysis": result,
            "properties_status": "completed"
        }
    except Exception as e:
        msg = f"Material properties analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "properties_status": "failed"
        }

async def analyze_logistics(state: AnalysisState) -> Dict:
    logger.info("Starting logistics analysis")
    if state.get("error"): return {}
    try:
        agent = LogisticCompatibilityAgent()
        result = await agent.analyze_top_logistics_materials(state["material_database"])
        return {
            "logistics_analysis": result,
            "logistics_status": "completed"
        }
    except Exception as e:
        msg = f"Logistics analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "logistics_status": "failed"
        }

async def analyze_costs(state: AnalysisState) -> Dict:
    logger.info("Starting cost analysis")
    if state.get("error"): return {}
    try:
        agent = ProductionCostAgent()
        result = await agent.analyze_production_costs(state["material_database"])
        return {
            "cost_analysis": result,
            "costs_status": "completed"
        }
    except Exception as e:
        msg = f"Cost analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "costs_status": "failed"
        }

async def analyze_sustainability(state: AnalysisState) -> Dict:
    logger.info("Starting sustainability analysis")
    if state.get("error"): return {}
    try:
        agent = EnvironmentalImpactAgent()
        result = await agent.analyze_environmental_impact(state["material_database"])
        return {
            "sustainability_analysis": result,
            "sustainability_status": "completed"
        }
    except Exception as e:
        msg = f"Sustainability analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "sustainability_status": "failed"
        }

async def analyze_consumer_behavior(state: AnalysisState) -> Dict:
    logger.info("Starting consumer behavior analysis")
    if state.get("error"): return {}
    try:
        agent = ConsumerBehaviorAgent()
        result = await agent.analyze_consumer_behavior(state["material_database"])
        return {
            "consumer_analysis": result,
            "consumer_status": "completed"
        }
    except Exception as e:
        msg = f"Consumer behavior analysis failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "consumer_status": "failed"
        }

def calculate_material_scores(
    material: Dict[str, Any],
    analyses: Dict[str, Dict[str, float]],
    weights: Dict[str, float],
    total_weight: float
) -> Dict[str, Any]:
    """Calculate normalized and weighted scores for a material."""
    try:
        key = material.get("material_name") or material.get("id") or material.get("name")
        if not key:
            raise ValueError("Material missing identifier")

        scores = {}
        total_score = 0
        
        for dim, analysis_scores in analyses.items():
            if dim not in weights:
                logger.warning(f"Missing weight for dimension: {dim}")
                continue
                
            raw_score = analysis_scores.get(key, 0)
            if not isinstance(raw_score, (int, float)):
                logger.warning(f"Invalid score type for {key} in {dim}: {type(raw_score)}")
                raw_score = 0
                
            weight = weights[dim]
            normalized = min(max(raw_score, 0), 100)
            weighted = normalized * weight
            
            scores[dim] = {
                "raw": raw_score,
                "normalized": round(normalized, 2),
                "weighted": round(weighted, 2),
                "weight": weight
            }
            total_score += weighted

        final_score = round(total_score / total_weight, 2) if total_weight > 0 else 0
        
        return {
            "total_score": final_score,
            "scores": scores,
            "reasoning": {
                "score_breakdown": scores,
                "strengths": [
                    {
                        "dimension": dim,
                        "score": score["normalized"],
                        "impact": round((score["weight"] / total_weight) * 100, 1)
                    }
                    for dim, score in scores.items()
                    if score["normalized"] >= 70
                ],
                "weaknesses": [
                    {
                        "dimension": dim,
                        "score": score["normalized"],
                        "impact": round((score["weight"] / total_weight) * 100, 1)
                    }
                    for dim, score in scores.items()
                    if score["normalized"] <= 30
                ],
                "contribution_analysis": {
                    dim: round((score["weighted"] / total_score * 100), 1)
                    for dim, score in scores.items()
                } if total_score > 0 else {
                    dim: round((score["weight"] / total_weight * 100), 1)
                    for dim, score in scores.items()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Score calculation failed for material {key}: {str(e)}", exc_info=True)
        return {
            "total_score": 0,
            "error": str(e),
            "scores": {},
            "reasoning": {
                "score_breakdown": {},
                "error_details": str(e)
            }
        }

async def orchestrate_results(state: AnalysisState) -> Dict:
    """Orchestrate the analysis results and generate final report."""
    logger.info("Starting results orchestration")
    try:
        orchestrator = OrchestrationAgent(CURRENT_TIME, CURRENT_USER)

        # Process materials
        materials = state["material_database"].get("materials", {})
        all_materials = []
        for crit_list in materials.values():
            all_materials.extend(crit_list)

        # Gather analysis scores from agent outputs (structured JSONs)
        consumer_scores = {
            m["material_name"]: m["overall_consumer_score"] * 10
            for m in state["consumer_analysis"].get("top_materials", [])
        }
        logistics_scores = {
            m["material_name"]: m["logistics_score"] * 10
            for m in state["logistics_analysis"].get("top_materials", [])
        }
        properties_scores = {
            m["material_name"]: m["overall_score"] * 10
            for m in state["properties_analysis"].get("top_materials", [])
        }
        cost_scores = {
            m["material_name"]: m["cost_score"] * 10
            for m in state["cost_analysis"].get("top_materials", [])
        }
        sustainability_scores = {
            m["material_name"]: m["environmental_score"] * 10
            for m in state["sustainability_analysis"].get("top_materials", [])
        }

        # Calculate scores with weights
        scored_materials = []
        for material in all_materials:
            name = material.get("material_name")
            if not name:
                continue

            scores = {
                "consumer": consumer_scores.get(name, 0),
                "logistics": logistics_scores.get(name, 0),
                "properties": properties_scores.get(name, 0),
                "cost": cost_scores.get(name, 0),
                "sustainability": sustainability_scores.get(name, 0),
            }

            total_score = sum(
                (scores[cat] * ANALYSIS_WEIGHTS[cat]) for cat in scores
            ) / sum(ANALYSIS_WEIGHTS.values())

            scored_materials.append({
                **material,
                **scores,
                "total_score": round(total_score, 2)
            })

        # Sort and select top materials
        scored_materials.sort(key=lambda x: x["total_score"], reverse=True)
        seen = set()
        top_materials = []
        for m in scored_materials:
            if m["material_name"] not in seen:
                top_materials.append(m)
                seen.add(m["material_name"])
            if len(top_materials) == 5:
                break

        # just before you call generate_executive_summary:
        product_name = state["input_data"]["product_name"]
        k = len(top_materials)  # number of top materials you're iterating over

        # Generate material-wise executive summaries
        material_summaries = []
        for material in top_materials:
            summary = await orchestrator.generate_executive_summary(
                product_name,
                k,
                material)
            material_summaries.append({
                "material_name": material["material_name"],
                "summary": summary})


        # Prepare final results
        final_results = {
            "product_name": state["input_data"]["product_name"],
            "timestamp": CURRENT_TIME,
            "user": CURRENT_USER,
            "weights_used": ANALYSIS_WEIGHTS,
            "top_materials": top_materials,
            "all_materials": scored_materials,
            "material_summaries": material_summaries,
        }

        # Save report
        report_path = orchestrator._save_report(final_results, "analysis_report")
        final_results["report_path"] = report_path

        return {
            "final_results": final_results,
            "orchestration_status": "completed"
        }

    except Exception as e:
        msg = f"Results orchestration failed: {str(e)}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "orchestration_status": "failed"
        }


async def handle_error(state: AnalysisState) -> Dict:
    """Handle errors and generate error reports."""
    logger.error(f"Error handler: {state.get('error', 'Unknown error')}")
    
    try:
        orchestrator = OrchestrationAgent(CURRENT_TIME, CURRENT_USER)

        status_info = {
            "input": state.get("input_status", "unknown"),
            "compatibility": state.get("compatibility_status", "unknown"),
            "material_db": state.get("material_db_status", "unknown"),
            "properties": state.get("properties_status", "unknown"),
            "logistics": state.get("logistics_status", "unknown"),
            "costs": state.get("costs_status", "unknown"),
            "sustainability": state.get("sustainability_status", "unknown"),
            "consumer": state.get("consumer_status", "unknown"),
            "orchestration": state.get("orchestration_status", "unknown")
        }

        error_analysis = await orchestrator.analyze_error(
            state.get("error", "Unknown error"),
            status_info
        )

        error_report = {
            "error": state.get("error", "Unknown error"),
            "user": CURRENT_USER,
            "timestamp": CURRENT_TIME,
            "status": status_info,
            "error_analysis": error_analysis
        }

        report_path = orchestrator._save_report(error_report, "error_report")
        error_report["report_path"] = report_path

        return {"final_results": error_report}

    except Exception as e:
        logger.critical(f"Error handler failed: {e}", exc_info=True)
        return {
            "final_results": {
                "error": f"Error handling failed: {str(e)}",
                "timestamp": CURRENT_TIME,
                "user": CURRENT_USER,
                "status": "critical_failure"
            }
        }

def route_after_material_db(state: AnalysisState) -> Literal["run_analyses", "handle_error"]:
    if state.get("error") or not state.get("material_database", {}).get("materials"):
        return "handle_error"
    return "run_analyses"

def check_analyses_completion(state: AnalysisState) -> Literal["orchestrate", "handle_error"]:
    if state.get("error"):
        return "handle_error"
    
    required_statuses = {
        "properties_status": "completed",
        "logistics_status": "completed",
        "costs_status": "completed",
        "sustainability_status": "completed",
        "consumer_status": "completed"
    }
    
    for status_key, expected_value in required_statuses.items():
        if state.get(status_key) != expected_value:
            return "handle_error"
            
    return "orchestrate"

def create_analysis_graph():
    """Create and configure the analysis workflow graph."""
    workflow = StateGraph(AnalysisState)

    # Add nodes
    workflow.add_node("input", process_input)
    workflow.add_node("compatibility", analyze_product_compatibility)
    workflow.add_node("material_db", query_material_database)
    workflow.add_node("properties", analyze_material_properties)
    workflow.add_node("logistics", analyze_logistics)
    workflow.add_node("costs", analyze_costs)
    workflow.add_node("sustainability", analyze_sustainability)
    workflow.add_node("consumer", analyze_consumer_behavior)
    workflow.add_node("orchestrator", orchestrate_results)
    workflow.add_node("error_handler", handle_error)

    # Linear flow
    workflow.add_edge("input", "compatibility")
    workflow.add_edge("compatibility", "material_db")

    # Branch after material_db
    workflow.add_conditional_edges(
        "material_db",
        route_after_material_db,
        {
            "run_analyses": "run_analyses",
            "handle_error": "error_handler"
        }
    )

    # Parallel analyses
    workflow.add_node("run_analyses", lambda s: {})
    for node in ["properties", "logistics", "costs", "sustainability", "consumer"]:
        workflow.add_edge("run_analyses", node)
    
    workflow.add_node("join_analyses", lambda s: {})
    for node in ["properties", "logistics", "costs", "sustainability", "consumer"]:
        workflow.add_edge(node, "join_analyses")
    
    workflow.add_conditional_edges(
        "join_analyses",
        check_analyses_completion,
        {
            "orchestrate": "orchestrator",
            "handle_error": "error_handler"
        }
    )
    
    workflow.add_edge("orchestrator", END)
    workflow.add_edge("error_handler", END)

    workflow.set_entry_point("input")
    return workflow.compile(checkpointer=MemorySaver())

def print_results(result: Dict[str, Any], thread_id: str):
    """Print analysis results including performance reviews for multiple materials."""
    if result.get("error") or result.get("final_results", {}).get("error"):
        error_info = result if result.get("error") else result.get("final_results", {})
        print("\nAnalysis Error Report")
        print("===================")
        print(f"Error: {error_info.get('error', 'Unknown error')}")
        print(f"Timestamp: {CURRENT_TIME}")
        print(f"Session ID: {thread_id}")

        if error_analysis := error_info.get("error_analysis", {}):
            print("\nError Analysis:")
            print("--------------")
            if root_cause := error_analysis.get("root_cause_analysis", {}):
                print(f"Likely Cause: {root_cause.get('likely_cause', 'Unknown')}")
                if factors := root_cause.get("contributing_factors", []):
                    print("\nContributing Factors:")
                    for factor in factors:
                        print(f"- {factor.get('factor', 'Unknown factor')} "
                              f"(Impact: {factor.get('impact', 'unknown')})")
        return

    results = result.get("final_results", {})
    print("\nMaterial Analysis Report")
    print("=======================")
    print(f"Session ID: {thread_id}")
    print(f"Timestamp: {CURRENT_TIME}")

    if materials := results.get("material_summaries", []):
        print("\nMaterial Analysis Report")
        print("========================")
        for i, entry in enumerate(materials, 1):
            name = entry.get("material_name", f"Material {i}")
            review = entry.get("summary", {})

            snapshot = review.get("executive_snapshot", "N/A")
            score    = review.get("composite_score", "N/A")
            strengths   = review.get("strengths", [])
            trade_offs  = review.get("trade_offs", [])
            sci = review.get("supply_chain_implications", {})
            rec = review.get("recommendation", {})

            print(f"\n{i}. Material: {name}")
            print("------------------------")
            print(f"Executive Snapshot: {snapshot}")
            print(f"Composite Score: {score}")

            if strengths:
                print("\n✅ Strengths & Alignment:")
                for j, s in enumerate(strengths, 1):
                    dim = s.get("dimension", "Unknown")
                    ins = s.get("insight", "")
                    print(f"{j}. {dim}: {ins}")

            if trade_offs:
                print("\n⚖️ Trade-off Analysis:")
                for j, t in enumerate(trade_offs, 1):
                    dim = t.get("dimension", "Unknown")
                    mit = t.get("mitigation", "")
                    print(f"{j}. {dim}: {mit}")

            if sci:
                print("\n📦 Supply-Chain Implications:")
                print(f"  • Costs     : {sci.get('costs', '')}")
                print(f"  • Logistics : {sci.get('logistics', '')}")
                print(f"  • Regulatory: {sci.get('regulatory', '')}")
                print(f"  • Consumer  : {sci.get('consumer', '')}")

            if rec:
                adopt = rec.get("adopt", False)
                just = rec.get("justification", "")
                gain = rec.get("sustainability_gain_percent", "N/A")
                delta = rec.get("cost_delta_percent", "N/A")
                print("\n📈 Strategic Recommendation:")
                print(f"  Adopt?            : {'Yes' if adopt else 'No'}")
                print(f"  Justification     : {just}")
                print(f"  Sustainability Δ% : {gain}")
                print(f"  Cost Δ%           : {delta}")



async def main():
    """Main execution function."""
    thread_id = f"{CURRENT_USER}-{int(datetime.now(timezone.utc).timestamp())}"
    
    # Set up logging
    log_filename = f"analysis_log_{CURRENT_TIME.replace(' ', '_').replace(':', '-')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger.info(f"Starting analysis session - Thread: {thread_id}")
    logger.info(f"Analysis timestamp: {CURRENT_TIME}")

    try:
        graph = create_analysis_graph()
        result = await graph.ainvoke(
            {},
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "timestamp": CURRENT_TIME,
                    "user": CURRENT_USER
                }
            }
        )

        # Print results
        print_results(result, thread_id)
        logger.info(f"Analysis completed successfully for {result.get('final_results', {}).get('product_name', 'Unknown product')}")

    except Exception as e:
        logger.critical(f"Fatal error in analysis execution: {e}", exc_info=True)
        print("\nFatal Error Report")
        print("=================")
        print(f"Error: {str(e)}")
        print(f"Timestamp: {CURRENT_TIME}")
        print(f"Session ID: {thread_id}")
        print("Please check the log file for detailed error information.")
        print(f"Log File: {log_filename}")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("temp_KB", exist_ok=True)
    os.makedirs("temp_KB/reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Update current time and user
    CURRENT_TIME = "2025-05-09 21:04:45"  # Updated with provided time
    
    # Run analysis
    asyncio.run(main())