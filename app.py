import streamlit as st
import asyncio
from datetime import datetime, timezone
import requests
import numpy as np
import pandas as pd
import altair as alt
from streamlit_lottie import st_lottie
import main as orchestrator

# Page configuration
st.set_page_config(
    page_title="Packaging Material Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS styling with improved aesthetics
st.markdown("""
<style>
    /* Main styles */
    .main-title {
        text-align: center;
        font-size: 3rem !important;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        font-weight: 700;
    }
    .subtitle {
        text-align: center;
        font-size: 1.3rem !important;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Cards and sections */
    .analysis-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 24px;
        border-left: 5px solid #2563eb;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .analysis-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }
    .material-header {
        font-size: 1.8rem;
        color: #1e3a8a;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .material-score-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        font-size: 1.2rem;
        font-weight: bold;
        color: white;
    }
    
    /* Detail sections */
    .detail-section {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        border: 1px solid #e2e8f0;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Item styling */
    .strength-item {
        background-color: #dcfce7;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #22c55e;
    }
    .weakness-item {
        background-color: #fee2e2;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #ef4444;
    }
    .use-case-item {
        background-color: #dbeafe;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #3b82f6;
    }
    
    /* Comparison chart styling */
    .comparison-chart {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    /* Table styling */
    .sustainability-table {
        width: 100%;
        border-collapse: collapse;
    }
    .sustainability-table th {
        background-color: #f1f5f9;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        color: #334155;
        border-bottom: 2px solid #e2e8f0;
    }
    .sustainability-table td {
        padding: 10px;
        border-bottom: 1px solid #e2e8f0;
    }
    .sustainability-table tr:hover {
        background-color: #f8fafc;
    }
    
    /* Form styling */
    .stForm {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    .stForm > div:first-child {
        padding-bottom: 0 !important;
    }
    div[data-testid="stForm"] {
        border: none !important;
    }
    .form-header {
        font-size: 1.5rem;
        color: #1e3a8a;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    /* Submit button styling */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 4px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    /* Progress animation */
    .progress-container {
        margin: 30px 0;
        text-align: center;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 40px;
        color: #64748b;
        font-size: 0.9rem;
        padding: 20px 0;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        height: 100%;
        border: 1px solid #e2e8f0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
        color: #1e3a8a;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Score gauge */
    .score-gauge {
        position: relative;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f5f9;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        border-bottom: 4px solid #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def get_score_color(score):
    """Return appropriate color based on score value."""
    if isinstance(score, str):
        try:
            score = float(score.replace('%', ''))
        except:
            return "#64748b"  # Default gray for non-numeric
    
    if score >= 85:
        return "#15803d"  # Dark green
    elif score >= 70:
        return "#65a30d"  # Light green
    elif score >= 50:
        return "#d97706"  # Orange
    else:
        return "#dc2626"  # Red

def create_gauge_chart(score):
    """Render a gauge chart using theta encoding instead of start/end angles."""
    # Normalize score to fraction 0–1
    if isinstance(score, str):
        try:
            score = float(score.replace('%', '')) / 100
        except:
            score = 0.5
    elif isinstance(score, (int, float)):
        if score > 1:
            score = score / 100
    score = max(0, min(score, 1))

    # DataFrames for background, gauge, and label
    bg_df = pd.DataFrame({'value': [1]})
    fg_df = pd.DataFrame({'value': [score]})
    text_df = pd.DataFrame({'score': [int(score * 100)]})

    # Full-circle background
    background = (
        alt.Chart(bg_df)
        .mark_arc(innerRadius=40, outerRadius=80, color='#e2e8f0')
        .encode(theta=alt.Theta('value:Q', stack=True))
        .properties(width=160, height=160)
    )

    # Foreground gauge arc
    foreground = (
        alt.Chart(fg_df)
        .mark_arc(innerRadius=40, outerRadius=80, color='#4C9A2A')
        .encode(theta=alt.Theta('value:Q', stack=True))
        .properties(width=160, height=160)
    )

    # Centered score text
    score_text = (
        alt.Chart(text_df)
        .mark_text(fontSize=24, fontWeight='bold', color='#1e3a8a')
        .encode(text='score:Q')
        .properties(width=160, height=160)
    )

    # Layer and return
    return alt.layer(background, foreground, score_text).configure_view(strokeWidth=0)

def create_comparison_chart(materials):
    """Create a comparison bar chart for all materials."""
    if not materials:
        return None
        
    data = []
    for material in materials:
        name = material.get("material_name", "Unknown")
        
        # Handle new structure where composite_score might be an object
        comp_score = material.get("summary", {}).get("composite_score", {})
        if isinstance(comp_score, dict):
            score_value = comp_score.get("composite", 0)
        else:
            score_value = comp_score
            
        # Convert score to numeric
        if isinstance(score_value, str):
            try:
                score_value = float(score_value.replace('%', ''))
            except ValueError:
                score_value = 0
        
        data.append({
            "Material": name,
            "Score": score_value
        })
    
    if not data:
        return None
        
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate the bar chart with Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Score:Q', title='Sustainability Score'),
        y=alt.Y('Material:N', title=None, sort='-x'),
        color=alt.Color('Score:Q', scale=alt.Scale(scheme='blueorange'), legend=None),
        tooltip=['Material', 'Score']
    ).properties(
        title='Material Comparison',
        width=600,
        height=min(len(data) * 40, 500)
    )
    
    return chart

def create_sustainability_comparison_table(materials):
    """Create a comparison table for sustainability metrics."""
    if not materials:
        return None
    
    # Extract metrics from each material
    table_data = []
    
    for material in materials:
        name = material.get("material_name", "Unknown")
        summary = material.get("summary", {})
        
        # Handle new structure where composite_score might be an object with metrics
        comp_score = summary.get("composite_score", {})
        
        if isinstance(comp_score, dict):
            metrics = comp_score.get("metrics", {})
            composite = comp_score.get("composite", "N/A")
        else:
            # For backward compatibility
            metrics = {}
            composite = comp_score
            
        # Prepare row data
        row_data = {"Material": name, "Overall Score": composite}
        
        # Add metrics
        for dim, data in metrics.items():
            dim_name = dim.replace('_', ' ').title()
            row_data[dim_name] = f"{data.get('value', 'N/A')} ({data.get('score', 'N/A')}/100)"
        
        table_data.append(row_data)
    
    return pd.DataFrame(table_data)

async def main():
    # Header with animation
    st.markdown('<h1 class="main-title">📦 Packaging Material Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover the perfect sustainable packaging for your product</p>', unsafe_allow_html=True)

    # Load and display animation
    lottie_packaging = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_ggwtezyt.json")
    if lottie_packaging:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_packaging, height=200, key="packaging_animation")

    # Interactive Input Form with improved styling
    st.markdown('<h3 class="form-header">🔍 Enter Product Details</h3>', unsafe_allow_html=True)
    
    with st.form("product_details"):
        tab1, tab2 = st.tabs(["📋 Basic Details", "📐 Dimensions & Budget"])
        
        with tab1:
            product_name = st.text_input("Product Name", placeholder="e.g., Eggs")
            packaging_location = st.text_input("Packaging Location", placeholder="e.g., Kolkata")
            units = st.number_input("Units per Shipment", min_value=1, value=100)
            
            # Additional guidance
            st.info("📝 Enter accurate location details for region-specific packaging recommendations.")
            
        with tab2:
            budget_col, _ = st.columns([1, 1])
            with budget_col:
                budget = st.number_input("Budget per Unit (USD)", min_value=0.0, value=10.0, format="%.2f")
            
            st.markdown("##### Product Dimensions")
            col1, col2, col3 = st.columns(3)
            with col1:
                length = st.number_input("Length (cm)", min_value=0.1, value=4.0)
            with col2:
                width = st.number_input("Width (cm)", min_value=0.1, value=4.0)
            with col3:
                height = st.number_input("Height (cm)", min_value=0.1, value=5.0)
                
            # Show volume calculation in real-time
            volume = length * width * height
            st.metric("Calculated Volume", f"{volume:.2f} cm³")

        submitted = st.form_submit_button("🔍 Analyze Materials")

    if submitted:
        # Prepare input data
        input_data = {
            "product_name": product_name,
            "units_per_shipment": units,
            "dimensions": {"length": length, "width": width, "height": height},
            "packaging_location": packaging_location,
            "budget_constraint": budget,
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": "codegeek03",
                "volume": length * width * height
            }
        }

        # Initialize analysis
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        thread_id = f"{orchestrator.CURRENT_USER}-{int(datetime.now(timezone.utc).timestamp())}"
        initial_state = {
            "input_data": input_data,
            "user_login": orchestrator.CURRENT_USER,
            "current_time": now,
        }

        # Show enhanced progress
        progress_container = st.container()
        
        with progress_container:
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # More detailed steps
            steps = [
                "Understanding product requirements...",
                "Analyzing material compatibility...",
                "Evaluating environmental factors...",
                "Checking regional availability in " + packaging_location + "...",
                "Assessing durability requirements...",
                "Calculating carbon footprint...",
                "Analyzing cost efficiency...",
                "Generating detailed analysis..."
            ]

            analysis_task = asyncio.create_task(
                orchestrator.create_analysis_graph().ainvoke(
                    initial_state,
                    config={"configurable": {"thread_id": thread_id}}
                )
            )

            for i, step in enumerate(steps):
                progress_value = (i + 1) / len(steps)
                progress_bar.progress(progress_value)
                status_text.markdown(f"<h4 style='text-align:center;color:#3b82f6;'>{step}</h4>", unsafe_allow_html=True)
                await asyncio.sleep(0.5)

            result = await analysis_task
            st.markdown('</div>', unsafe_allow_html=True)

        # Clear progress indicators
        progress_container.empty()

        if err := (result.get("error") or result.get("final_results", {}).get("error")):
            st.error(f"Analysis failed: {err}")
            
            # Display error analysis if available
            error_info = result if result.get("error") else result.get("final_results", {})
            if error_analysis := error_info.get("error_analysis", {}):
                st.markdown("### Error Analysis")
                if root_cause := error_analysis.get("root_cause_analysis", {}):
                    st.warning(f"**Likely Cause:** {root_cause.get('likely_cause', 'Unknown')}")
                    if factors := root_cause.get("contributing_factors", []):
                        st.markdown("#### Contributing Factors:")
                        for factor in factors:
                            st.markdown(f"- **{factor.get('factor', 'Unknown factor')}** "
                                      f"(Impact: {factor.get('impact', 'unknown')})")
        else:
            # Success animation
            success_col1, success_col2, success_col3 = st.columns([1, 2, 1])
            with success_col2:
                lottie_success = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_jbrw3hcz.json")
                if lottie_success:
                    st_lottie(lottie_success, height=150, key="success_animation")
            
            # Dashboard layout
            st.markdown("## 📊 Material Analysis Results")
            
            material_summaries = result.get("final_results", {}).get("material_summaries", [])
            
            if material_summaries:
                # Add the new sustainability comparison table
                st.markdown("### 📋 Sustainability Metrics Comparison")
                comparison_table = create_sustainability_comparison_table(material_summaries)
                if comparison_table is not None:
                    st.dataframe(comparison_table, use_container_width=True, hide_index=True)
                
                # Create comparison chart
                comparison_chart = create_comparison_chart(material_summaries)
                if comparison_chart:
                    st.markdown('<div class="comparison-chart">', unsafe_allow_html=True)
                    st.altair_chart(comparison_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display top 3 key metrics
                if len(material_summaries) >= 1:
                    st.markdown("### Key Sustainability Metrics")
                    metric_cols = st.columns(3)
                    
                    # Best option - adjusted for new structure
                    def get_composite_score(material):
                        comp_score = material.get("summary", {}).get("composite_score", {})
                        if isinstance(comp_score, dict):
                            return float(comp_score.get("composite", 0))
                        try:
                            return float(str(comp_score).replace('%', '') or 0)
                        except:
                            return 0
                    
                    best_material = max(material_summaries, key=get_composite_score)
                    best_name = best_material.get("material_name", "Unknown")
                    
                    # Handle new structure
                    comp_score = best_material.get("summary", {}).get("composite_score", {})
                    if isinstance(comp_score, dict):
                        best_score = comp_score.get("composite", "N/A")
                    else:
                        best_score = comp_score
                    
                    # Cost effective option - adjusted for new structure
                    def get_cost_delta(material):
                        rec = material.get("summary", {}).get("consulting_recommendation", {})
                        if not rec:
                            rec = material.get("summary", {}).get("recommendation", {})
                        delta = rec.get("cost_delta_percent", 0)
                        if delta == "N/A":
                            return 0
                        try:
                            return float(str(delta).replace('%', '') or 0)
                        except:
                            return 0
                    
                    cost_effective = min(material_summaries, key=get_cost_delta)
                    cost_name = cost_effective.get("material_name", "Unknown")
                    
                    rec = cost_effective.get("summary", {}).get("consulting_recommendation", {})
                    if not rec:
                        rec = cost_effective.get("summary", {}).get("recommendation", {})
                    cost_delta = rec.get("cost_delta_percent", "N/A")
                    
                    # Most sustainable gain - adjusted for new structure
                    def get_sustainability_gain(material):
                        rec = material.get("summary", {}).get("consulting_recommendation", {})
                        if not rec:
                            rec = material.get("summary", {}).get("recommendation", {})
                        gain = rec.get("sustainability_uplift_percent", rec.get("sustainability_gain_percent", 0))
                        if gain == "N/A":
                            return 0
                        try:
                            return float(str(gain).replace('%', '') or 0)
                        except:
                            return 0
                    
                    sustainable = max(material_summaries, key=get_sustainability_gain)
                    sustainable_name = sustainable.get("material_name", "Unknown")
                    
                    rec = sustainable.get("summary", {}).get("consulting_recommendation", {})
                    if not rec:
                        rec = sustainable.get("summary", {}).get("recommendation", {})
                    sustainable_gain = rec.get("sustainability_uplift_percent", rec.get("sustainability_gain_percent", "N/A"))
                    
                    with metric_cols[0]:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Top Recommended Material</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{best_name}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div>Score: {best_score}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with metric_cols[1]:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Most Cost-Effective</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{cost_name}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div>Cost Δ: {cost_delta}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with metric_cols[2]:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Highest Sustainability Gain</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{sustainable_name}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div>Gain: {sustainable_gain}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Display detailed material analysis
                for i, entry in enumerate(material_summaries[:5], 1):
                    name = entry.get("material_name", f"Material {i}")
                    review = entry.get("summary", {})

                    # Extract fields - updated for new structure
                    snapshot = review.get("executive_snapshot", "N/A")
                    
                    # Handle new composite score structure
                    comp_score = review.get("composite_score", {})
                    if isinstance(comp_score, dict):
                        score = comp_score.get("composite", "N/A")
                        metrics = comp_score.get("metrics", {})
                    else:
                        score = comp_score
                        metrics = {}
                    
                    reg_ctx = review.get("regulatory_context", review.get("regional_regulatory_context", "No regulatory context available."))
                    strengths = review.get("strengths", [])
                    trade_offs = review.get("trade_offs", [])
                    
                    # Handle supply chain implications
                    sci = review.get("supply_chain_implications", {})
                    
                    # Handle recommendation with new structure
                    rec = review.get("consulting_recommendation", {})
                    if not rec:  # Fallback to old structure
                        rec = review.get("recommendation", {})
                    
                    # Convert adopt/advice for backward compatibility
                    adopt = rec.get("adopt", False)
                    if "advice" in rec:
                        just = rec.get("advice", "")
                    else:
                        just = rec.get("justification", "")
                    
                    # Handle uplift/gain terminology changes
                    if "sustainability_uplift_percent" in rec:
                        gain = rec.get("sustainability_uplift_percent", "N/A")
                    else:
                        gain = rec.get("sustainability_gain_percent", "N/A")
                    
                    delta = rec.get("cost_delta_percent", "N/A")
                    
                    # Score color
                    score_color = get_score_color(score)

                    # Card container with score badge
                    st.markdown(f'''
                    <div class="analysis-card">
                        <h3 class="material-header">
                            <div class="material-score-circle" style="background-color: {score_color};">{i}</div>
                            {name}
                        </h3>
                    ''', unsafe_allow_html=True)

                    # Score visualization and executive snapshot
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Create gauge chart for score
                        try:
                            score_value = float(str(score).replace('%', '')) / 100 if isinstance(score, str) else score/100
                        except:
                            score_value = 0.5
                        gauge_chart = create_gauge_chart(score_value)
                        st.altair_chart(gauge_chart, use_container_width=True)
                        st.markdown(f"<div style='text-align:center;'><strong>Sustainability Score</strong></div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown("#### 📝 Executive Snapshot")
                        st.markdown(f"{snapshot}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Create tabs for detailed information
                    tabs = st.tabs(["📑 Overview", "⚖️ Trade-offs", "📦 Supply Chain", "📈 Recommendation"])
                    
                    with tabs[0]:  # Overview tab
                        # Display metrics breakdown if available
                        if metrics:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">📊 Composite Score Breakdown</div>', unsafe_allow_html=True)
                            for dim, data in metrics.items():
                                val = data.get("value", "")
                                dim_score = data.get("score", "")
                                st.markdown(f"* **{dim.replace('_', ' ').title()}**: {val} ➔ score {dim_score}/100")
                            st.markdown(f"* **Weighted Composite**: {score}/100")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Regional context
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">📍 Regional Regulatory Context</div>', unsafe_allow_html=True)
                        for line in reg_ctx.split("\n"):
                            st.markdown(f"> {line}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Strengths visualization
                        if strengths:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">✅ Strengths & Alignment</div>', unsafe_allow_html=True)
                            for s in strengths:
                                st.markdown(f"""
                                <div class="strength-item">
                                <strong>{s.get('dimension')}</strong><br/>
                                {s.get('insight')}
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                    with tabs[1]:  # Trade-offs tab
                        if trade_offs:
                            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">⚖️ Trade-off Analysis</div>', unsafe_allow_html=True)
                            for t in trade_offs:
                                st.markdown(f"""
                                <div class="weakness-item">
                                    <strong>{t.get('dimension')}</strong><br/>
                                    {t.get('mitigation')}
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                    with tabs[2]:  # Supply Chain tab
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">📦 Supply-Chain Implications</div>', unsafe_allow_html=True)
                        sc_cols = st.columns(2)
                        with sc_cols[0]:
                            st.markdown(f"""
                            <div class="detail-section">
                                <div class="section-title">💰 Costs</div>
                                <p>{sci.get('costs', 'No cost data available.')}</p>
                            </div>

                            <div class="detail-section">
                                <div class="section-title">🚚 Logistics</div>
                                <p>{sci.get('logistics', 'No logistics data available.')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with sc_cols[1]:
                            st.markdown(f"""
                            <div class="detail-section">
                                <div class="section-title">📜 Regulatory</div>
                                <p>{sci.get('regulatory', 'No regulatory data available.')}</p>
                            </div>
                            
                            <div class="detail-section">
                                <div class="section-title">👥 Consumer Perception</div>
                                <p>{sci.get('consumer', 'No consumer data available.')}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    with tabs[3]:  # Recommendation tab
                        # Calculate colors based on gain and delta
                        try:
                            gain_val = float(str(gain).replace('%', '')) if gain not in (None, "N/A") else 0
                        except:
                            gain_val = 0
                        uplift_color = "#15803d" if gain_val > 0 else "#dc2626"

                        try:
                            delta_val = float(str(delta).replace('%', '')) if delta not in (None, "N/A") else 0
                        except:
                            delta_val = 0
                        cost_color = "#dc2626" if delta_val > 0 else "#15803d"

                        st.markdown('<div class="detail-section use-case-item">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">🎯 Strategic Recommendation</div>', unsafe_allow_html=True)
                        st.markdown(f"{just}", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Uplift and cost delta
                        rec_cols = st.columns([1,1])
                        with rec_cols[0]:
                            st.markdown(f"""
                            <div class="detail-section">
                                <div class="section-title">♻️ Sustainability Impact</div>
                                <p style="font-size:1.5rem; font-weight:bold; color:{uplift_color};">
                                    {'+' if gain_val > 0 else ''}{gain}%
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        with rec_cols[1]:
                            st.markdown(f"""
                            <div class="detail-section">
                                <div class="section-title">💵 Cost Impact</div>
                                <p style="font-size:1.5rem; font-weight:bold; color:{cost_color};">
                                    {'+' if delta_val > 0 else ''}{delta}%
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

    # Footer and session info
    st.markdown("""
    <div class="footer">
        <p>Packaging analysis based on sustainability metrics, material properties, and regional availability.</p>
    """, unsafe_allow_html=True)



# Add a lightweight dark mode toggle
def add_dark_mode_toggle():
    dark_mode = st.sidebar.checkbox("Dark Mode", False)
    if dark_mode:
        st.markdown("""
        <style>
            :root {
                --background-color: #1a1a2e;
                --text-color: #e6e6e6;
                --card-background: #16213e;
                --section-background: #0f3460;
                --border-color: #1f4287;
                --highlight-color: #e94560;
            }
            
            body {
                background-color: var(--background-color);
                color: var(--text-color);
            }
            
            .main-title {
                color: #4cc9f0 !important;
            }
            
            .subtitle {
                color: #a5b4fc !important;
            }
            
            .analysis-card {
                background-color: var(--card-background);
                border-left: 5px solid #4361ee;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            .detail-section {
                background-color: var(--section-background);
                border: 1px solid var(--border-color);
            }
            
            .material-header {
                color: #4cc9f0 !important;
            }
            
            .section-title {
                color: #a5b4fc !important;
            }
            
            .stForm {
                background-color: var(--section-background);
                border: 1px solid var(--border-color);
            }
            
            .form-header {
                color: #4cc9f0 !important;
            }
            
            .footer {
                color: #a5b4fc !important;
                border-top: 1px solid var(--border-color);
            }
            
            /* Streamlit specific elements */
            .stTextInput > div > div > input {
                background-color: #253554;
                color: var(--text-color);
                border: 1px solid var(--border-color);
            }
            
            .stNumberInput > div > div > input {
                background-color: #253554;
                color: var(--text-color);
                border: 1px solid var(--border-color);
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: var(--section-background);
                color: var(--text-color);
                border: 1px solid var(--border-color);
            }
            
            .stTabs [aria-selected="true"] {
                background-color: var(--card-background) !important;
                border-bottom: 4px solid #4361ee !important;
            }
            
            .metric-card {
                background-color: var(--card-background);
                border: 1px solid var(--border-color);
            }
            
            .metric-value {
                color: #4cc9f0 !important;
            }
            
            .metric-label {
                color: #a5b4fc !important;
            }
        </style>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    asyncio.run(main())
    add_dark_mode_toggle()  # Add dark mode toggle in sidebar
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    thread_id = f"{orchestrator.CURRENT_USER}-{int(datetime.now(timezone.utc).timestamp())}"
    # Footer
    st.markdown(f"*Session ID: {thread_id} | Generated: {now}*", unsafe_allow_html=True)
    st.markdown("© 2025 Packaging Material Analysis System 🌱")
