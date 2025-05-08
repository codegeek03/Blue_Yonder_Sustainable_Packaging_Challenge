from typing import Dict, Any, List, Literal, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from datetime import datetime, timezone
import logging

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

class AnalysisState(TypedDict):
    input_data: Dict[str, Any]  # Remove Annotated as it's causing concurrent update issues
    compatibility_analysis: Dict[str, Any]
    material_database: Dict[str, Any]
    properties_analysis: Dict[str, Any]
    logistics_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    sustainability_analysis: Dict[str, Any]
    consumer_analysis: Dict[str, Any]
    final_results: Dict[str, Any]
    #error: NotRequired[Optional[str]]
    processing_status: Dict[str, str]
    user_login: str
    current_time: str

# Node definitions
async def process_input(state: AnalysisState) -> AnalysisState:
    logger.info("Starting input processing")
    try:
        # Create a new state dict to avoid concurrent modifications
        new_state = state.copy()
        
        if not new_state.get("input_data"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = CURRENT_USER
            agent = ProductInput(current_time=now, user_login=user)
            details = await agent.get_product_details()
            
            # Update all related fields at once
            new_state.update({
                "input_data": details,
                "processing_status": {"input": "completed", "timestamp": now, "user": user},
                "user_login": user,
                "current_time": now
            })
            
        return new_state
    except Exception as e:
        msg = f"Input processing failed: {e}"
        logger.error(msg, exc_info=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Return a new state with error information
        return {
            **state,
            "error": msg,
            "processing_status": {
                "input": "failed",
                "timestamp": now,
                "user": CURRENT_USER,
                "error_details": str(e)
            }
        }

async def analyze_product_compatibility(state: AnalysisState) -> AnalysisState:
    logger.info("Starting product compatibility analysis")
    try:
        if state.get("error"): return state
        agent = ProductCompatibilityAgent()
        result = await agent.analyze_product_compatibility(state["input_data"]["product_name"], state["input_data"])
        state["compatibility_analysis"] = result
        state["processing_status"]["compatibility"] = "completed"
        return state
    except Exception as e:
        msg = f"Product compatibility analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["compatibility"] = "failed"
        return state

async def query_material_database(state: AnalysisState) -> AnalysisState:
    logger.info("Starting material database query")
    try:
        if state.get("error"): return state
        now = state.get("current_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        user = state.get("user_login", CURRENT_USER)
        agent = PackagingMaterialsAgent(user_login=user, current_time=now)
        result = await agent.find_materials_by_criteria(state["compatibility_analysis"])
        if not result.get("materials"): raise ValueError("No compatible materials found")
        state["material_database"] = result
        state["processing_status"]["material_db"] = "completed"
        return state
    except Exception as e:
        msg = f"Material DB query failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["material_db"] = "failed"
        return state

# Routing
from langgraph.graph import START, END

def route_after_material_db(state: AnalysisState) -> Literal["run_analyses", "handle_error"]:
    if state.get("error") or not state.get("material_database", {}).get("materials"):
        return "handle_error"
    return "run_analyses"

# Further analysis nodes (properties, logistics, cost, sustainability, consumer)
async def analyze_material_properties(state: AnalysisState) -> AnalysisState:
    logger.info("Starting material properties analysis")
    if state.get("error"): return state
    try:
        agent = MaterialPropertiesAgent()
        state["properties_analysis"] = await agent.analyze_material_properties(state["material_database"])
        state["processing_status"]["properties"] = "completed"
        return state
    except Exception as e:
        msg = f"Material properties analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["properties"] = "failed"
        return state

async def analyze_logistics(state: AnalysisState) -> AnalysisState:
    logger.info("Starting logistics analysis")
    if state.get("error"): return state
    try:
        agent = LogisticCompatibilityAgent()
        state["logistics_analysis"] = await agent.analyze_top_logistics_materials(state["material_database"])
        state["processing_status"]["logistics"] = "completed"
        return state
    except Exception as e:
        msg = f"Logistics analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["logistics"] = "failed"
        return state

async def analyze_costs(state: AnalysisState) -> AnalysisState:
    logger.info("Starting cost analysis")
    if state.get("error"): return state
    try:
        agent = ProductionCostAgent()
        state["cost_analysis"] = await agent.analyze_production_costs(state["material_database"])
        state["processing_status"]["costs"] = "completed"
        return state
    except Exception as e:
        msg = f"Cost analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["costs"] = "failed"
        return state

async def analyze_sustainability(state: AnalysisState) -> AnalysisState:
    logger.info("Starting sustainability analysis")
    if state.get("error"): return state
    try:
        agent = EnvironmentalImpactAgent()
        state["sustainability_analysis"] = await agent.analyze_environmental_impact(state["material_database"])
        state["processing_status"]["sustainability"] = "completed"
        return state
    except Exception as e:
        msg = f"Sustainability analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["sustainability"] = "failed"
        return state

async def analyze_consumer_behavior(state: AnalysisState) -> AnalysisState:
    logger.info("Starting consumer behavior analysis")
    if state.get("error"): return state
    try:
        agent = ConsumerBehaviorAgent()
        state["consumer_analysis"] = await agent.analyze_consumer_behavior(state["material_database"])
        state["processing_status"]["consumer"] = "completed"
        return state
    except Exception as e:
        msg = f"Consumer behavior analysis failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["consumer"] = "failed"
        return state

# Join and orchestrate

def check_analyses_completion(state: AnalysisState) -> Literal["orchestrate", "handle_error"]:
    if state.get("error"): return "handle_error"
    keys = ["properties_analysis","logistics_analysis","cost_analysis","sustainability_analysis","consumer_analysis"]
    if any(not state.get(k) for k in keys):
        state["error"] = "Incomplete analyses before orchestration"
        return "handle_error"
    return "orchestrate"

async def orchestrate_results(state: AnalysisState) -> AnalysisState:
    logger.info("Starting results orchestration")
    # If any earlier step errored, short‐circuit
    if state.get("error"):
        return state

    try:
        # 1) Gather materials
        materials = state["material_database"].get("materials", {})
        # Flatten materials_by_criteria dict into a single list of material dicts
        all_materials = []
        for crit_list in materials.values():
            all_materials.extend(crit_list)

        if not all_materials:
            raise ValueError("No materials available for scoring")

        # 2) Build per‐material raw scores from each analysis
        #    Each analysis state has a .get("scores", {id: score}) mapping
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
                # all equal → mid‐point
                return {k: 50.0 for k in d}
            return {k: (v - lo) / (hi - lo) * 100 for k, v in d.items()}

        norm = {cat: normalize(scores) for cat, scores in analyses.items()}

        # 4) Score each material by weighted sum
        total_weight = sum(ANALYSIS_WEIGHTS.values())
        scored = []
        for mat in all_materials:
            # assume each material dict has a unique 'material_name' or 'id'
            key = mat.get("material_name") or mat.get("id")
            if not key:
                continue

            # get each normalized value (default 0)
            wprops = norm["properties"].get(key, 0) * ANALYSIS_WEIGHTS["properties"]
            wlog  = norm["logistics"].get(key, 0)   * ANALYSIS_WEIGHTS["logistics"]
            wcost = norm["cost"].get(key, 0)        * ANALYSIS_WEIGHTS["cost"]
            wsust = norm["sustainability"].get(key, 0) * ANALYSIS_WEIGHTS["sustainability"]
            wcons = norm["consumer"].get(key, 0)    * ANALYSIS_WEIGHTS["consumer"]

            total = (wprops + wlog + wcost + wsust + wcons) / total_weight

            scored.append({
                **mat,
                "total_score": round(total, 2),
                "normalized": {
                    "properties": round(norm["properties"].get(key, 0), 2),
                    "logistics":  round(norm["logistics"].get(key, 0), 2),
                    "cost":       round(norm["cost"].get(key, 0), 2),
                    "sustainability": round(norm["sustainability"].get(key, 0), 2),
                    "consumer":   round(norm["consumer"].get(key, 0), 2),
                },
                "weighted": {
                    "properties": round(wprops, 2),
                    "logistics":  round(wlog, 2),
                    "cost":       round(wcost, 2),
                    "sustainability": round(wsust, 2),
                    "consumer":   round(wcons, 2),
                }
            })

        # 5) Sort and pick top‐K
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        top_k = scored[:5]  # or whatever K you want

        # 6) Assemble final_results
        state["final_results"] = {
            "product_name": state["input_data"]["product_name"],
            "timestamp": state["current_time"],
            "user": state["user_login"],
            "weights_used": ANALYSIS_WEIGHTS,
            "top_materials": top_k,
            "all_materials": scored,
        }
        state["processing_status"]["orchestration"] = "completed"
        return state

    except Exception as e:
        msg = f"Results orchestration failed: {e}"
        logger.error(msg, exc_info=True)
        state["error"] = msg
        state["processing_status"]["orchestration"] = "failed"
        return state


async def handle_error(state: AnalysisState) -> AnalysisState:
    msg = state.get("error", "Unknown error")
    logger.error(f"Error handler: {msg}")
    state["final_results"] = {"error": msg, "user": CURRENT_USER, "status": state.get("processing_status", {})}
    return state

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
    workflow.add_conditional_edges("material_db", route_after_material_db, {"run_analyses": "run_analyses", "handle_error": "error_handler"})

    # parallel analyses
    workflow.add_node("run_analyses", lambda s: s)
    for node in ["properties","logistics","costs","sustainability","consumer"]:
        workflow.add_edge("run_analyses", node)
    workflow.add_node("join_analyses", lambda s: s)
    for node in ["properties","logistics","costs","sustainability","consumer"]:
        workflow.add_edge(node, "join_analyses")
    workflow.add_conditional_edges("join_analyses", check_analyses_completion, {"orchestrate": "orchestrator", "handle_error": "error_handler"})

    workflow.set_entry_point("input")
    return workflow.compile(checkpointer=MemorySaver())

# Main execution\
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
                print(f"{i}. {m['name']} – {m['total_score']:.2f}")
    except Exception as e:
        logger.critical(f"Fatal: {e}", exc_info=True)
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 