import streamlit as st
import json
import asyncio
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit_lottie
from streamlit_lottie import st_lottie
import requests
from typing import Dict, Any, List
import time

# Import our orchestrator
import main as orchestrator

# Page configuration
st.set_page_config(
    page_title="Packaging Material Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 3rem !important;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-top: 1rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.3rem !important;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .result-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .material-header {
        font-size: 1.4rem;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .score-badge {
        background-color: #27ae60;
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .category-header {
        font-size: 1.6rem;
        color: #2c3e50;
        margin: 20px 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f4;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Function to display a comparison radar chart
def create_radar_chart(materials: List[Dict[str, Any]]):
    categories = ['properties', 'logistics', 'cost', 'sustainability', 'consumer']
    fig = go.Figure()
    
    for material in materials:
        values = [material.get(cat, 0) for cat in categories]
        # Close the radar by repeating the first value
        values.append(values[0])
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],  # Close the loop
            fill='toself',
            name=material.get('material_name', 'Unknown Material')
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Material Performance Across Categories",
        height=500
    )
    
    return fig

# Function to create a comparison bar chart
def create_comparison_chart(materials: List[Dict[str, Any]]):
    material_names = [m.get('material_name', f"Material {i+1}") for i, m in enumerate(materials)]
    total_scores = [m.get('total_score', 0) for m in materials]
    
    fig = px.bar(
        x=material_names,
        y=total_scores,
        labels={'x': 'Material', 'y': 'Total Score'},
        title="Total Score Comparison",
        color=total_scores,
        color_continuous_scale='viridis',
        text=[f"{score:.2f}" for score in total_scores]
    )
    
    fig.update_layout(
        xaxis_title="Material",
        yaxis_title="Score",
        yaxis=dict(range=[0, 100]),
        height=400
    )
    
    return fig

# Function to create a comparison table
def create_comparison_table(materials: List[Dict[str, Any]]):
    data = []
    for material in materials:
        row = {
            'Material': material.get('material_name', 'Unknown'),
            'Total Score': f"{material.get('total_score', 0):.2f}",
            'Properties': f"{material.get('properties', 0):.1f}",
            'Logistics': f"{material.get('logistics', 0):.1f}",
            'Cost': f"{material.get('cost', 0):.1f}",
            'Sustainability': f"{material.get('sustainability', 0):.1f}",
            'Consumer': f"{material.get('consumer', 0):.1f}"
        }
        data.append(row)
    
    return pd.DataFrame(data)

# App Structure
async def main():
    # Header with animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-title">📦 Packaging Material Analysis</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Identify the optimal packaging materials for your product</p>', unsafe_allow_html=True)
    
    # Load and display animation
    lottie_packaging = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_ggwtezyt.json")
    if lottie_packaging:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_packaging, height=200, key="packaging_animation")
    
    # Default example input
    default_input = {
        "product_name": "eggs",
        "units_per_shipment": 450,
        "dimensions": {"length": 4.0, "width": 4.0, "height": 5.0},
        "packaging_location": "kolkata",
        "budget_constraint": 890.0,
        "metadata": {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": "codegeek03",
            "volume": 80.0
        }
    }
    
    # Two column layout for input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Enter your product details")
        input_text = st.text_area(
            "Product Input JSON",
            value=json.dumps(default_input, indent=2),
            height=300
        )
    
    with col2:
        st.markdown("### JSON Schema Guide")
        st.info("""
        **Required fields:**
        - `product_name`: Name of your product
        - `dimensions`: Object with length, width, height in cm
        - `budget_constraint`: Maximum cost per unit
        
        **Optional fields:**
        - `units_per_shipment`: Number of units per package
        - `packaging_location`: Production location
        - `metadata`: Additional information
        """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Run Analysis")
    
    if analyze_button:
        try:
            user_input = json.loads(input_text)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            return
        
        # Build initial state
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        thread_id = f"{orchestrator.CURRENT_USER}-{int(datetime.now(timezone.utc).timestamp())}"
        initial_state = {
            "input_data": user_input,
            "user_login": orchestrator.CURRENT_USER,
            "current_time": now,
        }
        
        # Show progress
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with progress_placeholder.container():
            progress_bar = st.progress(0)
            status_text = status_placeholder.text("Initializing analysis...")
            
            # Simulate progress with analytics steps
            steps = [
                "Loading product specifications...",
                "Analyzing product compatibility...",
                "Querying materials database...",
                "Analyzing material properties...",
                "Evaluating logistics compatibility...",
                "Calculating production costs...",
                "Assessing environmental impact...",
                "Analyzing consumer preferences...",
                "Generating final report..."
            ]
            
            # Run the actual analysis in background
            analysis_task = asyncio.create_task(
                orchestrator.create_analysis_graph().ainvoke(
                    initial_state, 
                    config={"configurable": {"thread_id": thread_id}}
                )
            )
            
            # Show animated progress
            for i, step in enumerate(steps):
                progress_value = (i + 1) / len(steps)
                progress_bar.progress(progress_value)
                status_placeholder.text(step)
                await asyncio.sleep(0.5)  # Simulated delay
            
            # Wait for actual analysis to complete
            result = await analysis_task
            
        # Clear the progress indicators
        progress_placeholder.empty()
        status_placeholder.empty()
        
        # Display results
        if err := (result.get("error") or result.get("final_results", {}).get("error")):
            st.error(f"Analysis failed: {err}")
            
            # Display error details if available
            error_info = result.get("final_results", {}).get("error_analysis", {})
            if error_info:
                with st.expander("Error Analysis"):
                    if root_cause := error_info.get("root_cause_analysis", {}):
                        st.markdown(f"**Likely Cause:** {root_cause.get('likely_cause', 'Unknown')}")
                        
                        if factors := root_cause.get("contributing_factors", []):
                            st.markdown("**Contributing Factors:**")
                            for factor in factors:
                                st.markdown(f"- {factor.get('factor', 'Unknown')} "
                                          f"(*Impact: {factor.get('impact', 'unknown')}*)")
                    
                    if recommendations := error_info.get("recovery_recommendations", []):
                        st.markdown("**Recommendations:**")
                        for rec in recommendations:
                            st.markdown(f"- {rec.get('action', 'Unknown')} "
                                      f"(*Priority: {rec.get('priority', 'unknown')}*)")
        else:
            # Success animation
            success_col1, success_col2, success_col3 = st.columns([1, 1, 1])
            with success_col2:
                lottie_success = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_jbrw3hcz.json")
                if lottie_success:
                    st_lottie(lottie_success, height=150, key="success_animation")
                st.success(f"Analysis complete for: **{result['final_results'].get('product_name', 'Unknown')}**")
            
            # Get the top materials
            final_results = result["final_results"]
            top_materials = final_results.get("top_materials", [])
            
            if top_materials:
                # Create materials dashboard with tabs
                st.markdown('<h2 class="category-header">Analysis Results</h2>', unsafe_allow_html=True)
                
                tabs = st.tabs(["Top Materials", "Comparison Charts", "Detailed Analysis"])
                
                # Tab 1: Top Materials List
                with tabs[0]:
                    for i, material in enumerate(top_materials[:5], 1):
                        mat_name = material.get('material_name', f"Material {i}")
                        total_score = material.get('total_score', 0)
                        
                        st.markdown(f"""
                        <div class="result-card">
                            <h3 class="material-header">{i}. {mat_name} <span class="score-badge">Score: {total_score:.2f}</span></h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Material details in expander
                        with st.expander("View Details"):
                            detail_col1, detail_col2 = st.columns(2)
                            
                            # Properties and scores
                            with detail_col1:
                                st.markdown("#### Category Scores")
                                for category in ['properties', 'logistics', 'cost', 'sustainability', 'consumer']:
                                    score = material.get(category, 0)
                                    st.markdown(f"**{category.capitalize()}:** {score:.1f}")
                            
                            # Strengths and weaknesses
                            with detail_col2:
                                if reasoning := material.get('reasoning', {}):
                                    st.markdown("#### Analysis")
                                    
                                    if strengths := reasoning.get('strengths', []):
                                        st.markdown("**Strengths:**")
                                        for strength in strengths[:3]:  # Show top 3
                                            st.markdown(f"- {strength.get('dimension', '')}: {strength.get('score', 0):.1f}")
                                    
                                    if weaknesses := reasoning.get('weaknesses', []):
                                        st.markdown("**Areas for Improvement:**")
                                        for weakness in weaknesses[:3]:  # Show top 3
                                            st.markdown(f"- {weakness.get('dimension', '')}: {weakness.get('score', 0):.1f}")
                
                # Tab 2: Comparison Charts
                with tabs[1]:
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        # Radar chart comparing all materials
                        radar_chart = create_radar_chart(top_materials[:5])
                        st.plotly_chart(radar_chart, use_container_width=True)
                    
                    with chart_col2:
                        # Bar chart showing total scores
                        bar_chart = create_comparison_chart(top_materials[:5])
                        st.plotly_chart(bar_chart, use_container_width=True)
                    
                    # Comparison table
                    st.markdown("### Material Comparison Table")
                    comparison_df = create_comparison_table(top_materials[:5])
                    st.dataframe(
                        comparison_df.style.highlight_max(subset=['Total Score'], axis=0, color='lightgreen'),
                        use_container_width=True
                    )
                
                # Tab 3: Detailed Analysis
                with tabs[2]:
                    if material_summaries := final_results.get("material_summaries", []):
                        for i, material in enumerate(material_summaries[:5], 1):
                            name = material.get("material_name", f"Material {i}")
                            mpr = material.get("summary", {}).get("material_performance_review", {})
                            
                            st.markdown(f"### {i}. {name}")
                            st.markdown(f"**Score:** {mpr.get('calculated_score', 'N/A')}")
                            
                            with st.expander("Detailed Analysis"):
                                st.markdown(f"**Ranking Justification:**\n> {mpr.get('ranking_justification', 'N/A')}")
                                
                                # Domain Strengths
                                if strengths := mpr.get("domain_strengths", []):
                                    st.markdown("#### ✅ Domain Strengths")
                                    for j, s in enumerate(strengths, 1):
                                        st.markdown(f"**{j}. {s.get('dimension')}**")
                                        st.markdown(f"- **Reason:** {s.get('reason_for_strength')}")
                                        st.markdown(f"- **Impact:** {s.get('impact_on_ranking')}")
                                
                                # Compensating Factors
                                if weaknesses := mpr.get("compensating_factors", []):
                                    st.markdown("#### ⚠️ Compensating Factors")
                                    for j, w in enumerate(weaknesses, 1):
                                        st.markdown(f"**{j}. {w.get('dimension')}**")
                                        st.markdown(f"- **Weakness:** {w.get('weakness_reason')}")
                                        st.markdown(f"- **Compensated By:** {w.get('compensated_by')}")
                                        st.markdown(f"- **Justification:** {w.get('justification')}")
                                
                                # Fit for Use
                                if fit := mpr.get("fit_for_use", {}):
                                    st.markdown("#### 🧪 Fit for Use")
                                    st.markdown(f"**Summary:**\n> {fit.get('summary')}")
                                    
                                    if use_cases := fit.get("suitable_use_cases", []):
                                        st.markdown("**Suitable Use Cases:**")
                                        for case in use_cases:
                                            st.markdown(f"- {case}")
            
            # Show session info in footer
            st.markdown("---")
            st.markdown(f"""
            <div class="footer">
                <p>Session ID: <code>{thread_id}</code> | Timestamp: {now} | User: {orchestrator.CURRENT_USER}</p>
                <p>© 2025 Packaging Material Analysis System</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    asyncio.run(main())