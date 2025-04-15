import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import asyncio
import time
from datetime import datetime
import sys
import re
from pathlib import Path

# Import the orchestrator
sys.path.append(".")
try:
    from paste import PackagingAnalysisOrchestrator
except ImportError:
    # If the import fails, we'll create a mock version for demo purposes
    class PackagingAnalysisOrchestrator:
        async def run_analysis_workflow(self, product_name):
            # This is a mock implementation for the Streamlit app demo
            await asyncio.sleep(2)  # Simulate processing time
            
            # Return mock data
            return {
                "product_name": product_name,
                "analysis_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "analyses": {
                    "materials": {
                        "materials": [
                            {"material_name": "Glass", "justification": "Excellent barrier properties", "score": 0.92},
                            {"material_name": "Recycled PET", "justification": "Good recyclability", "score": 0.85},
                            {"material_name": "Bioplastic", "justification": "Biodegradable", "score": 0.78},
                            {"material_name": "Aluminum", "justification": "Lightweight and durable", "score": 0.75},
                            {"material_name": "Paperboard", "justification": "Renewable resource", "score": 0.70}
                        ]
                    },
                    "environmental": {
                        "summary": {
                            "best_performers": ["Bioplastic", "Paperboard", "Recycled PET"],
                            "worst_performers": ["Virgin Plastic", "Mixed Materials"]
                        },
                        "materials_analysis": [
                            {
                                "carbon_footprint": {"Glass": 8, "Recycled PET": 5, "Bioplastic": 2, "Aluminum": 7, "Paperboard": 3},
                                "water_usage": {"Glass": 7, "Recycled PET": 4, "Bioplastic": 3, "Aluminum": 6, "Paperboard": 2},
                                "recyclability": {"Glass": 9, "Recycled PET": 8, "Bioplastic": 6, "Aluminum": 9, "Paperboard": 7}
                            }
                        ]
                    },
                    "logistics": {
                        "logistics_analysis": [
                            {
                                "metrics": {
                                    "weight_efficiency": {"details": "Glass is heavier than alternatives", "score": 5},
                                    "storage_efficiency": {"details": "Stackable but breakable", "score": 7},
                                    "transport_emissions": {"details": "Higher due to weight", "score": 4}
                                }
                            }
                        ],
                        "materials_comparison": {
                            "Glass": 5.5, "Recycled PET": 7.5, "Bioplastic": 8.0, "Aluminum": 8.2, "Paperboard": 7.8
                        }
                    },
                    "cost": {
                        "summary": {
                            "most_economical_materials": ["Paperboard", "Recycled PET", "Bioplastic"],
                            "cost_comparison": {
                                "Glass": 8.5, "Recycled PET": 5.2, "Bioplastic": 6.8, "Aluminum": 7.2, "Paperboard": 3.5
                            }
                        }
                    },
                    "properties": {
                        "summary": {
                            "by_property": {
                                "durability": ["Glass", "Aluminum", "Recycled PET"],
                                "barrier_properties": ["Glass", "Aluminum", "Recycled PET"],
                                "flexibility": ["Bioplastic", "Paperboard", "Recycled PET"]
                            }
                        },
                        "property_scores": {
                            "Glass": {"durability": 9, "barrier_properties": 10, "flexibility": 2, "temperature_resistance": 9},
                            "Recycled PET": {"durability": 7, "barrier_properties": 8, "flexibility": 7, "temperature_resistance": 6},
                            "Bioplastic": {"durability": 5, "barrier_properties": 6, "flexibility": 8, "temperature_resistance": 4},
                            "Aluminum": {"durability": 9, "barrier_properties": 10, "flexibility": 5, "temperature_resistance": 8},
                            "Paperboard": {"durability": 4, "barrier_properties": 3, "flexibility": 7, "temperature_resistance": 2}
                        }
                    },
                    "compatibility": {
                        "overall_score": 8,
                        "compatibility_breakdown": {
                            "Glass": 9, "Recycled PET": 8, "Bioplastic": 7, "Aluminum": 8, "Paperboard": 6
                        },
                        "concerns": ["Glass may be heavy for consumers", "Bioplastic has limited shelf life"]
                    }
                }
            }

        async def generate_summary_report(self, consolidated_report):
            # Mock implementation
            return f"""
            Comprehensive Packaging Analysis Report
            =====================================
            Product: {consolidated_report['product_name']}
            Analysis Date: {consolidated_report['analysis_timestamp']}
            
            Key Findings:
            - Most sustainable options: Bioplastic, Paperboard
            - Most cost-effective: Paperboard
            - Best physical properties: Glass, Aluminum
            - Best logistics efficiency: Recycled PET, Bioplastic
            """

# Set page configuration
st.set_page_config(
    page_title="Sustainable Packaging Analyzer",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px !important;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-header {
        font-size: 28px !important;
        font-weight: bold;
        color: #1976D2;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .section-header {
        font-size: 24px !important;
        font-weight: bold;
        color: #0D47A1;
        margin-top: 10px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .highlight {
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #2E7D32;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
st.markdown("<div class='main-header'>🌿 Sustainable Packaging Analyzer</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100?text=Eco+Packaging", use_column_width=True)
    st.markdown("### Analysis Controls")
    
    product_name = st.text_input("Enter Product Name:", value="Glass Bottle")
    
    col1, col2 = st.columns([2, 1])
    start_button = col1.button("🚀 Start Analysis", type="primary", disabled=st.session_state.analysis_running)
    reset_button = col2.button("🔄 Reset", type="secondary")
    
    if reset_button:
        st.session_state.report_data = None
        st.session_state.analysis_running = False
        st.session_state.analysis_complete = False
        st.session_state.current_stage = 0
        st.rerun()
    
    if start_button:
        st.session_state.analysis_running = True
        st.session_state.analysis_complete = False
        st.session_state.current_stage = 0
        # Add to history if not a duplicate
        if product_name not in [item['product'] for item in st.session_state.history]:
            st.session_state.history.append({
                'product': product_name, 
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    
    st.divider()
    st.markdown("### Recent Analyses")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"**{item['product']}** - {item['timestamp']}")
    else:
        st.info("No previous analyses")
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This application analyzes sustainable packaging options based on:
    - Environmental impact
    - Material properties
    - Cost considerations
    - Logistics efficiency
    - Product compatibility
    """)

# Main content
if st.session_state.analysis_running and not st.session_state.analysis_complete:
    stages = ['Analyzing Materials', 'Environmental Impact Assessment', 'Logistics Analysis', 
             'Cost Analysis', 'Material Properties Evaluation', 'Product Compatibility Check']
    
    st.markdown("<div class='sub-header'>Analysis Progress</div>", unsafe_allow_html=True)
    
    progress_bar = st.progress(st.session_state.current_stage / len(stages))
    st.markdown(f"**Current stage:** {stages[st.session_state.current_stage]}")
    
    # Simulating the analysis process
    async def run_analysis():
        orchestrator = PackagingAnalysisOrchestrator()
        
        # Run the analysis and get the results
        results = await orchestrator.run_analysis_workflow(product_name)
        
        # Generate summary report
        summary = await orchestrator.generate_summary_report(results)
        results['summary_report'] = summary
        
        return results
    
    placeholder = st.empty()
    
    with placeholder.container():
        for i in range(st.session_state.current_stage, len(stages)):
            st.session_state.current_stage = i
            progress_bar.progress((i + 1) / len(stages))
            st.markdown(f"**Current stage:** {stages[i]}")
            
            # Add loading animation for current stage
            with st.spinner(f"Processing {stages[i].lower()}..."):
                if i == len(stages) - 1:  # If it's the last stage
                    # Actually run the analysis on the last stage
                    results = asyncio.run(run_analysis())
                    st.session_state.report_data = results
                    st.session_state.analysis_complete = True
                    st.session_state.analysis_running = False
                    st.rerun()
                else:
                    time.sleep(1)  # Simulate processing time

# Display analysis results
if st.session_state.analysis_complete and st.session_state.report_data:
    data = st.session_state.report_data
    
    # Success message
    st.success(f"Analysis for {data['product_name']} completed successfully!")
    
    # Overview tab
    st.markdown("<div class='sub-header'>Analysis Overview</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Key Findings")
        st.markdown(data['summary_report'])
    
    with col2:
        st.markdown("### Overall Material Scores")
        
        # Calculate overall scores
        materials = data['analyses']['materials']['materials']
        env_scores = data['analyses']['environmental']['materials_analysis'][0]
        logistics_scores = data['analyses']['logistics']['materials_comparison']
        cost_scores = data['analyses']['cost']['summary']['cost_comparison']
        compat_scores = data['analyses']['compatibility']['compatibility_breakdown']
        
        # Combine scores
        overall_scores = {}
        for material in materials:
            mat_name = material['material_name']
            if mat_name in logistics_scores and mat_name in compat_scores:
                # Calculate weighted average (weights can be adjusted)
                overall_scores[mat_name] = (
                    material.get('score', 0.7) * 0.2 +  # Material score
                    (10 - env_scores.get('carbon_footprint', {}).get(mat_name, 5)) * 0.3 +  # Environmental (reversed)
                    logistics_scores.get(mat_name, 5) * 0.2 +  # Logistics
                    (10 - cost_scores.get(mat_name, 5)) * 0.15 +  # Cost (reversed)
                    compat_scores.get(mat_name, 5) * 0.15  # Compatibility
                )
        
        # Create pie chart of overall scores
        fig = px.pie(
            values=list(overall_scores.values()),
            names=list(overall_scores.keys()),
            title="Material Sustainability Score",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Create tabs for detailed analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Environmental Impact", 
        "💰 Cost Analysis", 
        "🔍 Material Properties", 
        "🚚 Logistics", 
        "✅ Compatibility"
    ])
    
    # 1. Environmental Impact Tab
    with tab1:
        st.markdown("<div class='section-header'>Environmental Impact Analysis</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Environmental metrics
            env_metrics = data['analyses']['environmental']['materials_analysis'][0]
            
            # Create a dataframe for the radar chart
            env_df = pd.DataFrame({
                'Material': [],
                'Metric': [],
                'Score': []
            })
            
            for metric, scores in env_metrics.items():
                for material, score in scores.items():
                    # For carbon footprint and water usage, lower is better, so invert the scale
                    if metric in ['carbon_footprint', 'water_usage']:
                        adjusted_score = 10 - score
                    else:
                        adjusted_score = score
                        
                    env_df = pd.concat([env_df, pd.DataFrame({
                        'Material': [material],
                        'Metric': [metric.replace('_', ' ').title()],
                        'Score': [adjusted_score]
                    })], ignore_index=True)
            
            # Create a radar chart
            fig = px.line_polar(
                env_df, 
                r="Score", 
                theta="Metric", 
                color="Material", 
                line_close=True,
                range_r=[0, 10],
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Best Environmental Performers")
            best_performers = data['analyses']['environmental']['summary']['best_performers']
            
            for i, material in enumerate(best_performers):
                st.markdown(f"**{i+1}. {material}**")
                
                # Show relevant properties
                if material in env_metrics.get('carbon_footprint', {}):
                    st.markdown(f"Carbon Footprint: {10 - env_metrics['carbon_footprint'][material]}/10")
                if material in env_metrics.get('recyclability', {}):
                    st.markdown(f"Recyclability: {env_metrics['recyclability'][material]}/10")
                st.markdown("---")
    
    # 2. Cost Analysis Tab
    with tab2:
        st.markdown("<div class='section-header'>Cost Analysis</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Get cost data
            cost_data = data['analyses']['cost']['summary']['cost_comparison']
            
            # Create a bar chart
            cost_df = pd.DataFrame({
                'Material': list(cost_data.keys()),
                'Cost Score': list(cost_data.values())
            })
            
            # Sort by cost (lower is better)
            cost_df = cost_df.sort_values('Cost Score')
            
            fig = px.bar(
                cost_df,
                x='Material',
                y='Cost Score',
                title='Material Cost Comparison (Lower is Better)',
                color='Cost Score',
                color_continuous_scale='Viridis_r'  # Reversed so that lower cost gets better color
            )
            fig.update_layout(xaxis_title="Material", yaxis_title="Cost Score (Lower is Better)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Most Economical Materials")
            economical_materials = data['analyses']['cost']['summary']['most_economical_materials']
            
            for i, material in enumerate(economical_materials):
                st.markdown(f"**{i+1}. {material}**")
                if material in cost_data:
                    st.markdown(f"Cost Score: {cost_data[material]}/10 (Lower is better)")
                st.markdown("---")
            
            st.markdown("#### Cost Factors")
            st.markdown("""
            - Raw material cost
            - Manufacturing process
            - Energy requirements
            - Scale of production
            - Material availability
            """)
    
    # 3. Material Properties Tab
    with tab3:
        st.markdown("<div class='section-header'>Material Properties Analysis</div>", unsafe_allow_html=True)
        
        # Get property data
        if 'property_scores' in data['analyses']['properties']:
            property_data = data['analyses']['properties']['property_scores']
            
            # Create dataframe for properties
            props_df = pd.DataFrame({
                'Material': [],
                'Property': [],
                'Score': []
            })
            
            for material, properties in property_data.items():
                for prop, score in properties.items():
                    props_df = pd.concat([props_df, pd.DataFrame({
                        'Material': [material],
                        'Property': [prop.replace('_', ' ').title()],
                        'Score': [score]
                    })], ignore_index=True)
            
            # Pivot the dataframe for heatmap
            heatmap_df = props_df.pivot(index="Material", columns="Property", values="Score")
            
            # Create a heatmap
            fig = px.imshow(
                heatmap_df, 
                text_auto=True,
                aspect="auto",
                color_continuous_scale='Viridis',
                title="Material Properties Comparison"
            )
            fig.update_layout(xaxis_title="Property", yaxis_title="Material")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top performers by property
            st.markdown("#### Top Performers by Property")
            
            if 'by_property' in data['analyses']['properties']['summary']:
                properties = data['analyses']['properties']['summary']['by_property']
                
                col1, col2 = st.columns(2)
                
                for i, (prop, materials) in enumerate(properties.items()):
                    with col1 if i % 2 == 0 else col2:
                        st.markdown(f"**{prop.replace('_', ' ').title()}**")
                        for j, mat in enumerate(materials[:3]):
                            st.markdown(f"{j+1}. {mat}")
                        st.markdown("---")
    
    # 4. Logistics Tab
    with tab4:
        st.markdown("<div class='section-header'>Logistics Efficiency Analysis</div>", unsafe_allow_html=True)
        
        logistics_data = data['analyses']['logistics']
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Overall logistics scores
            materials_comparison = logistics_data['materials_comparison']
            
            # Create a radar chart for logistics metrics
            if 'logistics_analysis' in logistics_data and logistics_data['logistics_analysis']:
                metrics = logistics_data['logistics_analysis'][0]['metrics']
                
                # Create a figure with subplots
                fig = go.Figure()
                
                for material, overall_score in materials_comparison.items():
                    # Add traces for each material
                    fig.add_trace(go.Scatterpolar(
                        r=[metrics.get(metric, {}).get('score', 5) for metric in metrics.keys()],
                        theta=[metric.replace('_', ' ').title() for metric in metrics.keys()],
                        fill='toself',
                        name=material
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10]
                        )
                    ),
                    showlegend=True,
                    title="Logistics Performance by Material"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Logistics Metrics")
            
            if 'logistics_analysis' in logistics_data and logistics_data['logistics_analysis']:
                metrics = logistics_data['logistics_analysis'][0]['metrics']
                
                for metric, details in metrics.items():
                    st.markdown(f"**{metric.replace('_', ' ').title()}**")
                    st.markdown(f"{details['details']}")
                    st.markdown(f"Score: {details['score']}/10")
                    st.markdown("---")
            
            st.markdown("#### Best Logistics Performers")
            # Sort materials by logistics score
            sorted_materials = sorted(
                materials_comparison.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for i, (material, score) in enumerate(sorted_materials[:3]):
                st.markdown(f"**{i+1}. {material}**")
                st.markdown(f"Overall Logistics Score: {score}/10")
                st.markdown("---")
    
    # 5. Compatibility Tab
    with tab5:
        st.markdown("<div class='section-header'>Product Compatibility Analysis</div>", unsafe_allow_html=True)
        
        compatibility_data = data['analyses']['compatibility']
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Create a gauge chart for overall compatibility
            overall_score = compatibility_data['overall_score']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Compatibility Score"},
                gauge={
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "#2E7D32" if overall_score >= 7 else "#FFA000" if overall_score >= 5 else "#C62828"},
                    'steps': [
                        {'range': [0, 4], 'color': "#FFCDD2"},
                        {'range': [4, 7], 'color': "#FFE0B2"},
                        {'range': [7, 10], 'color': "#C8E6C9"}
                    ]
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Material compatibility scores
            compat_breakdown = compatibility_data['compatibility_breakdown']
            
            compat_df = pd.DataFrame({
                'Material': list(compat_breakdown.keys()),
                'Compatibility Score': list(compat_breakdown.values())
            })
            
            # Sort by compatibility score
            compat_df = compat_df.sort_values('Compatibility Score', ascending=False)
            
            fig = px.bar(
                compat_df,
                x='Material',
                y='Compatibility Score',
                title='Material Compatibility Scores',
                color='Compatibility Score',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Product Compatibility Considerations")
            
            st.markdown(f"**Overall Score: {overall_score}/10**")
            
            if 'concerns' in compatibility_data:
                st.markdown("#### Potential Concerns")
                for concern in compatibility_data['concerns']:
                    st.markdown(f"- {concern}")
            
            st.markdown("#### Best Compatible Materials")
            sorted_compat = sorted(
                compat_breakdown.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for i, (material, score) in enumerate(sorted_compat[:3]):
                st.markdown(f"**{i+1}. {material}**")
                st.markdown(f"Compatibility Score: {score}/10")
                st.markdown("---")
    
    # Final conclusion and recommendation
    st.markdown("<div class='sub-header'>Recommendation</div>", unsafe_allow_html=True)
    
    # Calculate best overall material
    if overall_scores:
        best_material = max(overall_scores.items(), key=lambda x: x[1])[0]
        second_best = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)[1][0]
        
        st.markdown(f"<div class='highlight'>Based on comprehensive analysis, <b>{best_material}</b> is the most sustainable packaging option for <b>{data['product_name']}</b>, with <b>{second_best}</b> as a strong alternative.</div>", unsafe_allow_html=True)
        
        # Show final comparison of top materials
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Environmental Impact**")
            if best_material in env_metrics.get('carbon_footprint', {}):
                st.markdown(f"Carbon Footprint: {10 - env_metrics['carbon_footprint'][best_material]}/10")
            if best_material in env_metrics.get('recyclability', {}):
                st.markdown(f"Recyclability: {env_metrics['recyclability'][best_material]}/10")
        
        with col2:
            st.markdown(f"**Cost Efficiency**")
            if best_material in cost_data:
                st.markdown(f"Cost Score: {10 - cost_data[best_material]}/10")
        
        with col3:
            st.markdown(f"**Product Compatibility**")
            if best_material in compat_breakdown:
                st.markdown(f"Compatibility: {compat_breakdown[best_material]}/10")

else:
    # Show welcome message when no analysis is running
    if not st.session_state.analysis_running:
        st.markdown("""
        <div class='highlight'>
        <h3>Welcome to the Sustainable Packaging Analyzer!</h3>
        <p>Enter a product name in the sidebar and click "Start Analysis" to begin exploring sustainable packaging options.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### How it works")
            st.markdown("""
            1. Enter your product name
            2. Start the analysis
            3. Our AI analyzes multiple packaging materials
            4. Review detailed visualization reports
            5. Get sustainable packaging recommendations
            """)
        
        with col2:
            st.markdown("### What we analyze")
            st.markdown("""
            - **Environmental Impact**: Carbon footprint, recyclability, and water usage
            - **Material Properties**: Durability, flexibility, barrier properties
            - **Cost Analysis**: Production and scaling economics
            - **Logistics Efficiency**: Transportation and storage optimization
            - **Product Compatibility**: How well materials work with your product
            """)
        
        # Sample visualization to showcase the tool
        st.markdown("### Sample Visualization")
        
        # Create sample data
        materials = ['PET', 'Glass', 'Aluminum', 'Paper', 'Bioplastic']
        sustainability = [7.2, 6.8, 8.1, 8.5, 9.2]
        cost = [8.5, 7.2, 6.3, 4.5, 3.8]
        
        # Create sample figure
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=materials,
            y=sustainability,
            name='Sustainability Score',
            marker_color='#4CAF50'
        ))
        
        fig.add_trace(go.Bar(
            x=materials,
            y=cost,
            name='Cost Score (Lower is Better)',
            marker_color='#FFA000'
        ))
        
        fig.update_layout(
            title='Sample Material Comparison',
            xaxis_title='Material',
            yaxis_title='Score',
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Sustainable Packaging Analyzer - Making eco-friendly packaging decisions easier
    <br>© 2025 Eco-Packaging Solutions
</div>
""", unsafe_allow_html=True)