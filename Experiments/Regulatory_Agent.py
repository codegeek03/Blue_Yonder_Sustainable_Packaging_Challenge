"""
RegulatoryAgent.py - Web search-enabled agent for gathering regulatory information
about packaging materials as part of a sustainable packaging decision framework.

This agent focuses on:
1. Finding current regulations for various packaging materials
2. Identifying upcoming regulatory changes
3. Discovering regional variations in packaging regulations
4. Providing compliance requirements for different materials
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
import datetime
import json
import os
from typing import Dict, Any, List


class RegulatoryAgent:
    def __init__(self, model_id: str = "gemini-2.0-flash-exp", enable_markdown: bool = True):
        """Initialize the RegulatoryAgent with search capabilities.
        
        Args:
            model_id (str): The Gemini model ID to use
            enable_markdown (bool): Whether to enable markdown formatting in responses
        """
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
         # Get the absolute path to the existing agents folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # If this file is already in the agents folder, we can use the parent directory
        if os.path.basename(base_dir) == "agents":
            self.reports_dir = os.path.join(base_dir, "regulatory_reports")
        else:
            # Find the agents folder from the current working directory
            project_dir = os.path.dirname(base_dir)
            self.reports_dir = os.path.join(project_dir, "agents", "cost_final")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        
        # Track user and timestamp info
        self.user_login = "swaralipi04"
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize the agent with Gemini and DuckDuckGo search
        self.agent = Agent(
            model=Gemini(
                id=model_id,
                api_key=api_key
            ),
            description="You are a regulatory expert specializing in packaging materials regulations worldwide. "
                      "Your goal is to provide accurate, up-to-date information on regulations, "
                      "compliance requirements, and standards related to packaging materials "
                      "with a focus on sustainability and environmental impact.",
            tools=[DuckDuckGoTools()],
            show_tool_calls=False,
            markdown=enable_markdown
        )
        
        # Track the materials we've already researched
        self.researched_materials = {}
        
    def search_regulations(self, material: str, region: str = "global", focus_area: str = None) -> Dict[str, Any]:
        """Search for regulations about a specific packaging material.
        
        Args:
            material: The packaging material to research
            region: Geographic region for regulations. Defaults to "global".
            focus_area: Specific regulatory aspect (e.g., "disposal", "recycling"). 
                       Defaults to None for comprehensive search.
        
        Returns:
            Dict containing structured information about regulations for the material
        """
        # Create a cache key for this specific query
        cache_key = f"{material.lower()}_{region.lower()}_{focus_area if focus_area else 'general'}"
        
        # Check if we've already researched this material+region+focus combination
        if cache_key in self.researched_materials:
            print(f"Using cached regulatory information for {material} in {region}")
            return self.researched_materials[cache_key]
        
        # Construct search query based on parameters
        search_query = f"Current {region} regulations for {material} packaging"
        if focus_area:
            search_query += f" {focus_area} requirements"
            
        search_query += " sustainability environmental"
            
        # Formulate a detailed prompt for the agent
        prompt = f"""
        I need comprehensive information about regulations for {material} packaging materials 
        {f'in {region}' if region != 'global' else 'globally'}.
        
        Please search for and provide:
        1. Current major regulations affecting {material} packaging 
        {f'specifically regarding {focus_area}' if focus_area else ''}
        2. Any upcoming regulatory changes or proposed legislation
        3. Compliance requirements and standards
        4. Sustainability implications of these regulations
        5. How these regulations compare to those for alternative materials
        
        Format the response as structured information suitable for a decision framework.
        Include specific regulation names, dates, and requirements where possible.
        """
        
        # Get response from the agent
        response = self.agent.print_response(prompt, stream=False)
        
        # Process and structure the response
        structured_info = self._structure_regulatory_info(response, material, region, focus_area)
        
        # Cache the result
        self.researched_materials[cache_key] = structured_info
        
        # Save to file for persistence
        self._save_to_report(structured_info, f"{material}_{region}_{focus_area if focus_area else 'general'}")
        
        return structured_info
    
    def _structure_regulatory_info(self, raw_response: str, material: str, region: str, focus_area: str) -> Dict[str, Any]:
        """Structure the raw response into a consistent format.
        
        Args:
            raw_response: The raw markdown response from the agent
            material: The packaging material
            region: The geographical region
            focus_area: The specific regulatory focus area
            
        Returns:
            Dict containing structured regulatory information
        """
        # Process the raw markdown response to extract key information
        timestamp = datetime.datetime.now().isoformat()
        
        # Create the structural framework for the response
        structured_info = {
            "material": material,
            "region": region,
            "focus_area": focus_area if focus_area else "general",
            "timestamp": timestamp,
            "user": self.user_login,
            "raw_response": raw_response,
            "regulatory_summary": {
                "current_regulations": [],
                "upcoming_changes": [],
                "compliance_requirements": [],
                "sustainability_implications": []
            },
            "comparison_to_alternatives": {}
        }
        
        # In a production environment, we would further process the raw_response
        # to extract specific regulatory details more systematically
        
        return structured_info
    
    def compare_materials(self, materials_list: List[str], region: str = "global") -> Dict[str, Any]:
        """Compare regulations across multiple packaging materials.
        
        Args:
            materials_list: List of materials to compare
            region: Geographic region for regulations. Defaults to "global".
            
        Returns:
            Dict containing comparative regulatory assessment of materials
        """
        comparison = {}
        
        for material in materials_list:
            comparison[material] = self.search_regulations(material, region)
            
        # Generate a comparative analysis
        prompt = f"""
        Based on the regulatory information about {', '.join(materials_list)} in {region},
        provide a comparative analysis highlighting:
        
        1. Which material faces the strictest regulations?
        2. Which material has the most upcoming regulatory changes?
        3. Which material has the most favorable regulatory status for sustainability?
        4. What are the key regulatory differences between these materials?
        
        Format the response as a comparative summary suitable for decision-making.
        """
        
        comparative_analysis = self.agent.print_response(prompt, stream=False)
        
        result = {
            "individual_assessments": comparison,
            "comparative_analysis": comparative_analysis,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": self.user_login
        }
        
        # Save comparison to file
        self._save_to_report(result, f"comparison_{region}_{'_'.join(materials_list)}")
        
        return result
    
    def get_regional_variations(self, material: str, regions_list: List[str]) -> Dict[str, Any]:
        """Identify regional variations in regulations for a packaging material.
        
        Args:
            material: The packaging material to research
            regions_list: List of regions to compare
            
        Returns:
            Dict containing assessment of regional variations in regulations
        """
        regional_data = {}
        
        for region in regions_list:
            regional_data[region] = self.search_regulations(material, region)
            
        # Generate an analysis of regional variations
        prompt = f"""
        Based on the regulatory information about {material} packaging in {', '.join(regions_list)},
        provide an analysis of regional variations highlighting:
        
        1. Which region has the strictest regulations for {material}?
        2. What are the key differences in how {material} is regulated across these regions?
        3. Are there regions where {material} faces significantly less regulation?
        4. How do sustainability requirements for {material} vary by region?
        
        Format the response as a regional comparison suitable for global packaging strategy.
        """
        
        regional_analysis = self.agent.print_response(prompt, stream=False)
        
        result = {
            "material": material,
            "regional_data": regional_data,
            "regional_analysis": regional_analysis,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": self.user_login
        }
        
        # Save regional analysis to file
        self._save_to_report(result, f"{material}_regional_{'_'.join(regions_list)}")
        
        return result
    
    def get_compliance_recommendations(self, material: str, region: str = "global") -> Dict[str, Any]:
        """Get specific recommendations for compliance with regulations.
        
        Args:
            material: The packaging material
            region: Geographic region. Defaults to "global".
            
        Returns:
            Dict containing compliance recommendations
        """
        # First get the general regulatory information
        regulatory_info = self.search_regulations(material, region)
        
        # Now ask for specific compliance recommendations
        prompt = f"""
        Based on the regulatory information about {material} packaging in {region},
        provide specific compliance recommendations:
        
        1. What are the essential steps for ensuring compliance with regulations?
        2. What documentation or certifications are required?
        3. What testing or validation is needed for {material} packaging?
        4. What are common compliance pitfalls or challenges with {material}?
        5. How can a company demonstrate sustainability compliance for {material}?
        
        Format the response as actionable compliance guidelines.
        """
        
        compliance_recommendations = self.agent.print_response(prompt, stream=False)
        
        result = {
            "material": material,
            "region": region,
            "regulatory_overview": regulatory_info,
            "compliance_recommendations": compliance_recommendations,
            "timestamp": datetime.datetime.now().isoformat(),
            "user": self.user_login
        }
        
        # Save compliance recommendations to file
        self._save_to_report(result, f"{material}_{region}_compliance")
        
        return result
    
    def _save_to_report(self, data: Dict[str, Any], filename: str) -> None:
        """Save regulatory data to a JSON file.
        
        Args:
            data: The regulatory data to save
            filename: Base filename to save to (without extension)
        """
        # Create a timestamp-based filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{self.reports_dir}/{filename}_{timestamp}.json"
        
        with open(full_filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {full_filename}")
    
    def load_from_json(self, filepath: str) -> Dict[str, Any]:
        """Load regulatory data from a JSON file.
        
        Args:
            filepath: Full path to the file to load from
            
        Returns:
            Dict containing the loaded data
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Report file not found: {filepath}")
            
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data


# Example usage
if __name__ == "__main__":
    # Create the regulatory agent
    agent = RegulatoryAgent()
    
    # Example: Get regulations for plastic packaging
    plastic_regs = agent.search_regulations("plastic", region="EU", focus_area="single-use")
    print(f"Found information about plastic regulations in EU")
    
    # Example: Compare different materials
    materials_comparison = agent.compare_materials(["plastic", "paper", "biodegradable polymer", "glass"], 
                                                 region="global")
    print(f"Completed materials comparison analysis")