import os
import re
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import json
import os
from typing import Dict, Any
from datetime import datetime
from agno.tools.tavily import TavilyTools
from agno.tools.calculator import CalculatorTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.pubmed import PubmedTools
import logging
from agno.tools.thinking import ThinkingTools
from agno.tools.knowledge import KnowledgeTools
import os
from agno.agent import Agent
from agno.knowledge.url import UrlKnowledge
from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.google import GeminiEmbedder


# Constants
CURRENT_USER = "codegeek03"
CURRENT_TIME = "2025-05-09 21:01:46"  # Updated with provided time

ANALYSIS_WEIGHTS = {
    "properties": 1.0,
    "logistics": 0.8,
    "cost": 1.2,
    "sustainability": 1.8,
    "consumer": 1.5
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

agno_docs = UrlKnowledge(
    urls = [
    # Existing sources
    "https://www.researchgate.net/publication/322808541_Sustainable_Packaging",
    "https://sustainablepackaging.org/wp-content/uploads/2019/06/Definition-of-Sustainable-Packaging.pdf",
    "https://s3.amazonaws.com/gb.assets/SPC+DG_1-8-07_FINAL.pdf",

    # New additions
    "https://www.materiom.org/",
    "https://infoguides.rit.edu/packaging/databases",
    "https://search.library.wisc.edu/catalog/9914150907202121",
    "https://www.repository.cam.ac.uk/items/7abbf7a8-c0d0-4169-8f03-c42b29a1ff95",
    "https://www.nal.usda.gov/research-tools/food-safety-research-projects/sustainable-and-active-packaging-food-product-safety",
    "https://www.packworld.com/sustainable-packaging/article/13346852/detailrich-sustainable-packaging-product-database-is-an-industry-first",
    "https://guacamoleairplane.com/supplier-guide",
    "https://domo.design/sustainable-packaging-resource-directory/",
    "https://www.walmartsustainabilityhub.com/waste/sustainable-packaging/resources",
    "https://www.billerud.com/sustainability/reporting-and-data/packaging-sustainability-tool",
    "https://www.sciencedirect.com/science/article/pii/S0959652624035820",
    "https://www.sciencedirect.com/science/article/pii/S2405844024001531",
    "https://www.sciencedirect.com/science/article/pii/S275380952400098X",
    "https://www.sciencedirect.com/science/article/abs/pii/S014181302402350X",

    # Additional authoritative resources
    "https://foodpackagingforum.org/resources",
    "https://www.researchgate.net/publication/47355743_Sustainable_food_packaging",
    "https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2018.00121/full",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC10788806/",
    "https://www.mdpi.com/2304-8158/13/11/1744",
    "https://researchonline.ljmu.ac.uk/id/eprint/25448/",
    "https://www.sciencedirect.com/science/article/pii/S2772502223000938",
    "https://blog.openfoodfacts.org/en/news/data-on-over-10000-packagings-to-explore",
    "https://www.sciencedirect.com/journal/future-foods/special-issue/10BKF9ZG01B",
    "https://hse.aws.openrepository.com/handle/10147/636294",
    "https://www.heraldopenaccess.us/openaccess/active-polymeric-packaging-innovation-in-food-with-potential-use-of-sustainable-raw-material",
    "https://arxiv.org/abs/2501.14764",
    "https://arxiv.org/abs/2311.16932"
],

    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=GeminiEmbedder(),
    ),
)

knowledge_tools = KnowledgeTools(
    knowledge=agno_docs,
    think=True,   
    search=True,  
    analyze=True,  
    add_few_shot=True, 
)

logger = logging.getLogger(__name__)

class PackagingMaterialsAgent:
    def __init__(
        self,
        user_login: str,
        current_time: str,
        model_id: str = "gemini-2.0-flash-exp",
        enable_markdown: bool = True
    ):
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.reports_dir = "temp_KB"
        os.makedirs(self.reports_dir, exist_ok=True)

        self.user_login = user_login
        self.current_time = current_time
        self.agent = Agent(
    model=Gemini(
        id="gemini-2.0-flash-exp",
        search=True,  
        grounding=False,
        temperature=0.2 # Disable grounding to allow tools and reasoning to work
    ),
    tools=[
        knowledge_tools
    ],
    description="You are an expert research analyst with exceptional analytical and investigative abilities.",
    instructions=[
        "ONLY include materials originally intended for packaging — DO NOT include accessories (e.g., labels, preservatives, adhesives, seals, inks).",
        "Materials must be scientifically accurate, currently in commercial use, and relevant to the specific product."
    ],
    reasoning=True,  # Enable reasoning 
    markdown=True,
    show_tool_calls=True
)

    def get_formatted_timestamp(self) -> str:
        return self.current_time

    def _save_report_to_file(self, data: Dict[str, Any], report_type: str) -> str:
        timestamp = self.current_time.replace(" ", "_").replace(":", "-")
        filename = f"{report_type}_{timestamp}.json"
        path = os.path.join(self.reports_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return path

    async def find_materials_by_criteria(
        self,
        compatibility_analysis: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            criteria = compatibility_analysis.get("criteria", {})
            product_name = compatibility_analysis.get("product_name", "")
            packaging_location = compatibility_analysis.get("packaging_location", "")
            units_per_shipment = compatibility_analysis.get("units_per_shipment", 0)\
            

            # Build minimal JSON schema for materials_by_criteria
            schema = {
                "materials_by_criteria": {
                    key: [
                        {
                            "material_name": "string",
                            "properties": "string"
                        }
                    ] * 10
                    for key in criteria
                },
                "analysis_timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_name,
                "packaging_location": packaging_location,
                "units_per_shipment": units_per_shipment
            }

            prompt = (
    f"You are a packaging sustainability specialist.\n"
    f"Focus on materials with proven low environmental impact, circularity, and compliance with industry standards.\n\n"
    f"Given the product '{product_name}', return packaging materials in EXACTLY the following JSON schema with NO extra keys, NO explanations, and NO deviations:\n\n"
    f"{json.dumps(schema, indent=2)}\n\n"
    f"PRIORITY GUIDELINES:\n"
    f"- Only include materials originally intended for sustainable packaging of {product_name}.\n"
    f"- Do NOT include accessories (labels, adhesives, inks, etc.).\n"
    f"- Avoid redundant entries (e.g., treat polypropylene and PP film as the same material).\n"
    f"- Materials must be scientifically accurate and currently in commercial use.\n\n"
    f"REPLY WITH VALID JSON ONLY — NO COMMENTS OR TEXT OUTSIDE THE JSON.\n\n"
    f"Reference these authoritative resources:\n"
    f"- https://www.materiom.org/\n"
    f"- https://infoguides.rit.edu/packaging/databases\n"
)



            # Call LLM
            response = await self.agent.arun(prompt)
            text = response.content.strip()
            # strip markdown fences
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]

            # Parse JSON with fallback for trailing commas
            try:
                analysis = json.loads(text)
            except json.JSONDecodeError:
                cleaned = re.sub(r',\s*([\]}])', r'\1', text)
                analysis = json.loads(cleaned)

            result = {
                "materials": analysis.get("materials_by_criteria", {}),
                "analysis_timestamp": self.current_time,
                "user_login": self.user_login,
                "product_name": product_name,
                "status": "completed"
            }

            result["report_path"] = self._save_report_to_file(result, "materials_analysis")
            return result

        except Exception as e:
            logger.error(f"Material analysis failed: {e}", exc_info=True)
            error_data = {
                "error": f"Analysis failed: {e}",
                "timestamp": self.current_time,
                "user_login": self.user_login,
                "status": "failed"
            }
            self._save_report_to_file(error_data, "error_materials_analysis")
            return error_data

    async def generate_materials_report(self, analysis: Dict[str, Any]) -> str:
        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        report_lines = [
            "Packaging Materials Analysis Report",
            "================================",
            f"Product: {analysis['product_name']}",
            f"Date: {analysis['analysis_timestamp']}",
            f"User: {analysis['user_login']}",
            "",
            "Materials by Criteria:",
            "---------------------",
        ]

        for crit, mats in analysis.get('materials', {}).items():
            report_lines.append(f"\n{crit.replace('_',' ').title()}:")
            for i, m in enumerate(mats, 1):
                report_lines.append(f"{i}. {m.get('material_name','')}\n   Props: {m.get('properties','')}\n   App: {m.get('application','')}")

        return "\n".join(report_lines) 