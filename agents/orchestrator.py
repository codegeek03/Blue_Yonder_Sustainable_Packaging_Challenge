from typing import Dict, Any, List, Literal, TypedDict, Annotated, Optional, NotRequired, Union
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from datetime import datetime, timezone
import logging
from langgraph.prebuilt import ToolNode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import all your agents
from detail_input import ProductInput
from Product_Analyst import ProductCompatibilityAgent
from MaterialDB_agent import PackagingMaterialsAgent
from Material_Analyst import MaterialPropertiesAgent
from Logistics_Analyst import LogisticCompatibilityAgent
from Sourcing_Cost_Analyser import ProductionCostAgent
from Sustainability_Analyst import EnvironmentalImpactAgent
from Consumer_Behaviour_Analyst import ConsumerBehaviorAgent

# Constants
CURRENT_USER = "codegeek03"
ANALYSIS_WEIGHTS = {
    "properties": 1.0,
    "logistics": 0.8,
    "cost": 1.2,
    "sustainability": 1.0,
    "consumer": 1.5
}

# Properly define AnalysisState with Annotated fields for concurrent updates
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
    # Make each status field independently updatable
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

# Node definitions
async def process_input(state: AnalysisState) -> Dict:
    logger.info("Starting input processing")
    try:
        # No need to copy state with Annotated fields
        if not state.get("input_data"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = CURRENT_USER
            agent = ProductInput(current_time=now, user_login=user)
            details = await agent.get_product_details()
            
            # Update only relevant fields
            return {
                "input_data": details,
                "input_status": "completed",
                "user_login": user,
                "current_time": now
            }
        return {}
    except Exception as e:
        msg = f"Input processing failed: {e}"
        logger.error(msg, exc_info=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "error": msg,
            "input_status": "failed"
        }

async def analyze_product_compatibility(state: AnalysisState) -> Dict:
    logger.info("Starting product compatibility analysis")
    try:
        if state.get("error"): return {}
        agent = ProductCompatibilityAgent()
        result = await agent.analyze_product_compatibility(state["input_data"]["product_name"], state["input_data"])
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
        now = state.get("current_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        user = state.get("user_login", CURRENT_USER)
        agent = PackagingMaterialsAgent(user_login=user, current_time=now)
        result = await agent.find_materials_by_criteria(state["compatibility_analysis"])
        if not result.get("materials"): raise ValueError("No compatible materials found")
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

# Routing
from langgraph.graph import START, END

def route_after_material_db(state: AnalysisState) -> Literal["run_analyses", "handle_error"]:
    if state.get("error") or not state.get("material_database", {}).get("materials"):
        return "handle_error"
    return "run_analyses"

# Further analysis nodes (properties, logistics, cost, sustainability, consumer)
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

# Join and orchestrate
def check_analyses_completion(state: AnalysisState) -> Literal["orchestrate", "handle_error"]:
    if state.get("error"): return "handle_error"
    
    # Check each analysis status individually
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

async def orchestrate_results(state: AnalysisState) -> Dict:
    logger.info("Starting results orchestration")
    if state.get("error"):
        return {}

    try:
        # 1) Gather materials
        materials = state["material_database"].get("materials", {})
        all_materials = []
        for crit_list in materials.values():
            all_materials.extend(crit_list)

        if not all_materials:
            raise ValueError("No materials available for scoring")

        # 2) Build per-material raw scores from each analysis
        analyses = {
            "properties": state["properties_analysis"].get("scores", {}),
            "logistics": state["logistics_analysis"].get("scores", {}),
            "cost": state["cost_analysis"].get("scores", {}),
            "sustainability": state["sustainability_analysis"].get("scores", {}),
            "consumer": state["consumer_analysis"].get("scores", {})
        }

        # 3) Normalize each category to [0,100]
        def normalize(d: Dict[str, float]):
            if not d:
                return {}
            vals = list(d.values())
            lo, hi = min(vals), max(vals)
            if lo == hi:
                return {k: 50.0 for k in d}
            return {k: (v - lo) / (hi - lo) * 100 for k, v in d.items()}

        norm = {cat: normalize(scores) for cat, scores in analyses.items()}

        # 4) Score each material with detailed reasoning
        total_weight = sum(ANALYSIS_WEIGHTS.values())
        scored = []
        for mat in all_materials:
            key = mat.get("material_name") or mat.get("id") or mat.get("name")
            if not key:
                continue

            # Get each normalized value and weighted score
            scores = {
                "properties": {
                    "normalized": round(norm["properties"].get(key, 0), 2),
                    "weighted": round(norm["properties"].get(key, 0) * ANALYSIS_WEIGHTS["properties"], 2),
                    "weight": ANALYSIS_WEIGHTS["properties"]
                },
                "logistics": {
                    "normalized": round(norm["logistics"].get(key, 0), 2),
                    "weighted": round(norm["logistics"].get(key, 0) * ANALYSIS_WEIGHTS["logistics"], 2),
                    "weight": ANALYSIS_WEIGHTS["logistics"]
                },
                "cost": {
                    "normalized": round(norm["cost"].get(key, 0), 2),
                    "weighted": round(norm["cost"].get(key, 0) * ANALYSIS_WEIGHTS["cost"], 2),
                    "weight": ANALYSIS_WEIGHTS["cost"]
                },
                "sustainability": {
                    "normalized": round(norm["sustainability"].get(key, 0), 2),
                    "weighted": round(norm["sustainability"].get(key, 0) * ANALYSIS_WEIGHTS["sustainability"], 2),
                    "weight": ANALYSIS_WEIGHTS["sustainability"]
                },
                "consumer": {
                    "normalized": round(norm["consumer"].get(key, 0), 2),
                    "weighted": round(norm["consumer"].get(key, 0) * ANALYSIS_WEIGHTS["consumer"], 2),
                    "weight": ANALYSIS_WEIGHTS["consumer"]
                }
            }

            # Calculate total score
            total = sum(dim["weighted"] for dim in scores.values()) / total_weight

            # Generate reasoning report
            strengths = []
            weaknesses = []
            for dimension, score in scores.items():
                if score["normalized"] >= 70:
                    strengths.append({
                        "dimension": dimension,
                        "score": score["normalized"],
                        "impact": round((score["weight"] / total_weight) * 100, 1)
                    })
                elif score["normalized"] <= 30:
                    weaknesses.append({
                        "dimension": dimension,
                        "score": score["normalized"],
                        "impact": round((score["weight"] / total_weight) * 100, 1)
                    })

            # Calculate contribution analysis safely
            contribution_analysis = {}
            if total > 0:  # Only calculate contributions if total is non-zero
                contribution_analysis = {
                    dim: round((scores[dim]["weighted"] / total) * 100, 1)
                    for dim in scores
                }
            else:  # If total is zero, set equal contributions based on weights
                total_weight = sum(scores[dim]["weight"] for dim in scores)
                contribution_analysis = {
                    dim: round((scores[dim]["weight"] / total_weight) * 100, 1)
                    if total_weight > 0 else 0
                    for dim in scores
                }

            reasoning = {
                "summary": f"Material achieved an overall score of {round(total, 2)} out of 100",
                "strengths": strengths,
                "weaknesses": weaknesses,
                "score_breakdown": scores,
                "contribution_analysis": contribution_analysis
            }

            scored.append({
                **mat,
                "total_score": round(total, 2),
                "reasoning": reasoning
            })

        # 5) Sort and pick top-K with comparative analysis
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        top_k = scored[:5]

        # 6) Add comparative analysis for top materials
        # Handle the case where we have no valid scores
        if scored:
            avg_scores = {
                dim: sum(mat["reasoning"]["score_breakdown"][dim]["normalized"] 
                        for mat in scored) / len(scored)
                for dim in ["properties", "logistics", "cost", "sustainability", "consumer"]
            }
        else:
            avg_scores = {
                dim: 0 for dim in ["properties", "logistics", "cost", "sustainability", "consumer"]
            }

        for mat in top_k:
            comparative = {
                dim: {
                    "vs_avg": round(mat["reasoning"]["score_breakdown"][dim]["normalized"] - avg_scores[dim], 1),
                    "percentile": round(sum(1 for s in scored 
                        if s["reasoning"]["score_breakdown"][dim]["normalized"] <= 
                        mat["reasoning"]["score_breakdown"][dim]["normalized"]) / max(len(scored), 1) * 100, 1)
                }
                for dim in ["properties", "logistics", "cost", "sustainability", "consumer"]
            }
            mat["reasoning"]["comparative_analysis"] = comparative

        # 7) Assemble final_results with enhanced reasoning
        return {
            "final_results": {
                "product_name": state["input_data"]["product_name"],
                "timestamp": state["current_time"],
                "user": state["user_login"],
                "weights_used": ANALYSIS_WEIGHTS,
                "top_materials": top_k,
                "all_materials": scored,
                "analysis_summary": {
                    "total_materials_analyzed": len(scored),
                    "average_scores": avg_scores,
                    "score_distribution": {
                        "excellent": len([m for m in scored if m["total_score"] >= 80]),
                        "good": len([m for m in scored if 60 <= m["total_score"] < 80]),
                        "fair": len([m for m in scored if 40 <= m["total_score"] < 60]),
                        "poor": len([m for m in scored if m["total_score"] < 40])
                    }
                }
            },
            "orchestration_status": "completed"
        }

    except Exception as e:
        msg = f"Results orchestration failed: {e}"
        logger.error(msg, exc_info=True)
        return {
            "error": msg,
            "orchestration_status": "failed"
        }
    
async def handle_error(state: AnalysisState) -> Dict:
    msg = state.get("error", "Unknown error")
    logger.error(f"Error handler: {msg}")
    
    # Collect all status information
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
    
    return {
        "final_results": {
            "error": msg, 
            "user": state.get("user_login", CURRENT_USER), 
            "status": status_info
        }
    }

# Graph builder
def create_analysis_graph():
    workflow = StateGraph(AnalysisState)

    # add nodes
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

    # linear flow: input → compatibility → material_db
    workflow.add_edge("input", "compatibility")
    workflow.add_edge("compatibility", "material_db")

    # branch after material_db
    workflow.add_conditional_edges("material_db", route_after_material_db, {
        "run_analyses": "run_analyses", 
        "handle_error": "error_handler"
    })

    # parallel analyses
    workflow.add_node("run_analyses", lambda s: {})  # Return empty dict to avoid state modifications
    for node in ["properties", "logistics", "costs", "sustainability", "consumer"]:
        workflow.add_edge("run_analyses", node)
    workflow.add_node("join_analyses", lambda s: {})  # Return empty dict to avoid state modifications
    for node in ["properties", "logistics", "costs", "sustainability", "consumer"]:
        workflow.add_edge(node, "join_analyses")
    workflow.add_conditional_edges("join_analyses", check_analyses_completion, {
        "orchestrate": "orchestrator", 
        "handle_error": "error_handler"
    })
    
    workflow.add_edge("orchestrator", END)
    workflow.add_edge("error_handler", END)

    workflow.set_entry_point("input")
    return workflow.compile(checkpointer=MemorySaver())

# Main execution
async def main():
    now = datetime.now(timezone.utc)
    thread_id = f"{CURRENT_USER}-{int(now.timestamp())}"
    logger.info(f"Thread: {thread_id}")

    graph = create_analysis_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await graph.ainvoke({}, config=config)
        if result.get("error") or (res := result.get("final_results", {})).get("error"):
            err = result.get("error") or res.get("error")
            print(f"Error: {err}")
        else:
            out = result["final_results"]
            print(f"Analysis complete for: {out['product_name']}")
            for i, m in enumerate(out.get("top_materials", []), 1):
                print(f"{i}. {m.get('name', m.get('material_name', m.get('id', 'Unknown')))} ")
    except Exception as e:
        logger.critical(f"Fatal: {e}", exc_info=True)
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())