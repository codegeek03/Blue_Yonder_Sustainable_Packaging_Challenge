from pydantic import BaseModel
from typing import Dict, List, Optional

class ProductInput(BaseModel):
    product_name: str

class MaterialClass(BaseModel):
    class_name: str
    description: str
    sub_materials: List[str]
    reasoning: str

class PrimaryClassSelection(BaseModel):
    selected_class: str
    sub_materials: List[str]
    reasoning: str

class MaterialScore(BaseModel):
    score: float
    details: str

class SubMaterialEvaluation(BaseModel):
    material_name: str
    quality_score: Optional[float] = None
    environmental_score: Optional[float] = None
    regulatory_score: Optional[float] = None
    consumer_score: Optional[float] = None
    logistics_cost_score: Optional[float] = None
    details: str

class FinalRecommendation(BaseModel):
    primary_class: str
    best_sub_material: str
    overall_scores: Dict[str, float]
    explanation: str
    detailed_analysis: Dict[str, Dict[str, float]]