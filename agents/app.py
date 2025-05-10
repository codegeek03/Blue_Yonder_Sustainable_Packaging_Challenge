import streamlit as st
import asyncio
from datetime import datetime, timezone
import requests
from streamlit_lottie import st_lottie
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
    .analysis-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .material-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-bottom: 15px;
    }
    .detail-section {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .strength-item {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .weakness-item {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .use-case-item {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

async def main():
    # Header
    st.markdown('<h1 class="main-title">📦 Packaging Material Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover the perfect packaging material for your product</p>', unsafe_allow_html=True)

    # Load and display animation
    lottie_packaging = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_ggwtezyt.json")
    if lottie_packaging:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st_lottie(lottie_packaging, height=200, key="packaging_animation")

    # Interactive Input Form
    st.markdown("### Product Details")
    with st.form("product_details"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., Eggs")
            packaging_location = st.text_input("Packaging Location", placeholder="e.g., Kolkata")
            budget = st.number_input("Budget per Unit (USD)", min_value=0.0, value=10.0)

        with col2:
            units = st.number_input("Units per Shipment", min_value=1, value=100)
            col2_1, col2_2, col2_3 = st.columns(3)
            with col2_1:
                length = st.number_input("Length (cm)", min_value=0.1, value=4.0)
            with col2_2:
                width = st.number_input("Width (cm)", min_value=0.1, value=4.0)
            with col2_3:
                height = st.number_input("Height (cm)", min_value=0.1, value=5.0)

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

        # Show progress
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        with progress_placeholder.container():
            progress_bar = st.progress(0)
            status_text = status_placeholder.text("Initializing analysis...")

            steps = [
                "Understanding product requirements...",
                "Analyzing material compatibility...",
                "Evaluating environmental factors...",
                "Checking regional availability...",
                "Assessing durability requirements...",
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
                status_placeholder.text(step)
                await asyncio.sleep(0.5)

            result = await analysis_task

        # Clear progress indicators
        progress_placeholder.empty()
        status_placeholder.empty()

        if err := (result.get("error") or result.get("final_results", {}).get("error")):
            st.error(f"Analysis failed: {err}")
        else:
            # Success animation
            success_col1, success_col2, success_col3 = st.columns([1, 2, 1])
            with success_col2:
                lottie_success = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_jbrw3hcz.json")
                if lottie_success:
                    st_lottie(lottie_success, height=150, key="success_animation")

            # Display Detailed Analysis
                        # Display Detailed Analysis
            st.markdown("## Material Analysis Results")
            
            if material_summaries := result.get("final_results", {}).get("material_summaries", []):
                for i, entry in enumerate(material_summaries[:5], 1):
                    name = entry.get("material_name", f"Material {i}")
                    review = entry.get("summary", {})

                    # Extract the new fields
                    snapshot = review.get("executive_snapshot", "N/A")
                    score    = review.get("composite_score", "N/A")
                    strengths   = review.get("strengths", [])
                    trade_offs  = review.get("trade_offs", [])
                    sci = review.get("supply_chain_implications", {})
                    rec = review.get("recommendation", {})

                    # Card container
                    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                    st.markdown(f'<h3 class="material-header">{i}. {name}</h3>', unsafe_allow_html=True)

                    # Executive Snapshot & Score
                    st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                    st.markdown(f"**Executive Snapshot:** {snapshot}")
                    st.markdown(f"**Composite Score:** {score}")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Strengths & Alignment
                    if strengths:
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown("#### ✅ Strengths & Alignment")
                        for s in strengths:
                            st.markdown(f"""
                            <div class="strength-item">
                              <strong>{s.get('dimension')}</strong><br/>
                              {s.get('insight')}
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Trade‐off Analysis
                    if trade_offs:
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown("#### ⚖️ Trade‐off Analysis")
                        for t in trade_offs:
                            st.markdown(f"""
                            <div class="weakness-item">
                              <strong>{t.get('dimension')}</strong><br/>
                              Mitigation: {t.get('mitigation')}
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Supply‐Chain Implications
                    if sci:
                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown("#### 📦 Supply‐Chain Implications")
                        st.markdown(f"- **Costs:** {sci.get('costs','')}")
                        st.markdown(f"- **Logistics:** {sci.get('logistics','')}")
                        st.markdown(f"- **Regulatory:** {sci.get('regulatory','')}")
                        st.markdown(f"- **Consumer:** {sci.get('consumer','')}")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Strategic Recommendation
                    if rec:
                        adopt = rec.get("adopt", False)
                        just  = rec.get("justification", "")
                        gain  = rec.get("sustainability_gain_percent", "N/A")
                        delta = rec.get("cost_delta_percent", "N/A")

                        st.markdown('<div class="detail-section">', unsafe_allow_html=True)
                        st.markdown("#### 📈 Strategic Recommendation")
                        st.markdown(f"- **Adopt?** {'✅ Yes' if adopt else '❌ No'}")
                        st.markdown(f"- **Justification:** {just}")
                        st.markdown(f"- **Estimated Sustainability Δ%:** {gain}")
                        st.markdown(f"- **Estimated Cost Δ%:** {delta}")
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)  # close card


            # Footer
            st.markdown("---")
            st.markdown(f"""
            <div class="footer">
                <p>Analysis ID: <code>{thread_id}</code> | Generated: {now}</p>
                <p>© 2025 Packaging Material Analysis System</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    asyncio.run(main())


    