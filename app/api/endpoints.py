from fastapi import APIRouter, HTTPException
from app.core.models import ProductInput, FinalRecommendation
from app.agents.research import ResearchAgent
from app.agents.quality import QualityAgent
from app.agents.environmental import EnvironmentalAgent
from app.agents.regulatory import RegulatoryAgent
from app.agents.logistics import LogisticsAgent
from app.agents.orchestrator import OrchestratorAgent

# Create the router instance
router = APIRouter()

@router.post("/get-packaging", response_model=FinalRecommendation)
async def get_packaging_recommendation(product: ProductInput):
    try:
        # Initialize agents
        research_agent = ResearchAgent()
        quality_agent = QualityAgent()
        environmental_agent = EnvironmentalAgent()
        regulatory_agent = RegulatoryAgent()
        logistics_agent = LogisticsAgent()
        orchestrator = OrchestratorAgent()

        # Step 1: Initial research of primary material classes
        material_classes = await research_agent.initial_research(product.product_name)
        
        # Step 2: Select best primary class
        primary_selection = await research_agent.select_primary_class(
            product.product_name,
            material_classes
        )
        
        # Extract selected class and its sub-materials
        primary_class = primary_selection["selected_class"]
        sub_materials = primary_selection["sub_materials"]

        # Step 3: Evaluate specific materials within selected class
        quality_scores = await quality_agent.evaluate(
            product.product_name,
            primary_class,
            sub_materials
        )
        
        environmental_scores = await environmental_agent.evaluate(
            primary_class,
            sub_materials
        )
        
        regulatory_scores = await regulatory_agent.evaluate(
            product.product_name,
            primary_class,
            sub_materials
        )
        
        logistics_scores = await logistics_agent.evaluate(
            primary_class,
            sub_materials
        )

        # Step 4: Final decision by orchestrator
        final_recommendation = await orchestrator.decide(
            product_name=product.product_name,
            primary_class=primary_class,
            sub_materials=sub_materials,
            quality_scores=quality_scores,
            environmental_scores=environmental_scores,
            regulatory_scores=regulatory_scores,
            logistics_scores=logistics_scores
        )

        # Include all data for UI visualization
        return {
            **final_recommendation,
            "material_classes": material_classes,
            "sub_materials": sub_materials
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing recommendation: {str(e)}"
        )