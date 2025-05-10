import streamlit as st
import json
import asyncio
from datetime import datetime, timezone

# Import orchestrator
import main as orchestrator

st.set_page_config(page_title="Packaging Material Analysis", layout="wide")

st.title("📦 Packaging Material Analysis")

st.markdown(
    "Enter your product details in JSON and click **Run Analysis** to get the top materials."  
)

# Default example input
default_input = {
    "product_name": "eggs",
    "units_per_shipment": 450,
    "dimensions": {"length": 4.0, "width": 4.0, "height": 5.0},
    "packaging_location": "kolkata",
    "budget_constraint": 890.0,
    "metadata": {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": "codegeek03", "volume": 80.0}
}

# Input area
input_text = st.text_area(
    "Product Input JSON",
    value=json.dumps(default_input, indent=2),
    height=200
)

if st.button("Run Analysis"):
    try:
        user_input = json.loads(input_text)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
    else:
        # Build initial state
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        thread_id = f"{orchestrator.CURRENT_USER}-{int(datetime.now(timezone.utc).timestamp())}"
        initial_state = {
            "input_data": user_input,
            "user_login": orchestrator.CURRENT_USER,
            "current_time": now,
        }

        # Show spinner while running
        with st.spinner("Analyzing materials..."):
            graph = orchestrator.create_analysis_graph()
            # Use sync invocation via asyncio
            result = asyncio.run(graph.ainvoke(initial_state, config={
                "configurable": {"thread_id": thread_id}
            }))

        # Display results
        if err := (result.get("error") or result.get("final_results", {}).get("error")):
            st.error(f"Analysis failed: {err}")
        else:
            final = result["final_results"]
            st.success(f"Analysis complete for: {final.get('product_name', 'Unknown')} 🎉")

            top = final.get("top_materials", [])
            st.subheader(f"Top {len(top)} Materials")
            for i, mat in enumerate(top, 1):
                st.markdown(f"**{i}. {mat.get('name', mat.get('material_name',''))}** — Score: {mat.get('total_score',0):.2f}")
                with st.expander("Details"):
                    st.json({
                        "normalized_scores": mat.get("normalized", {}),
                        "weighted_scores": mat.get("weighted", {}),
                        "properties": mat.get("properties"),
                        "application": mat.get("application")
                    })

        st.write("---")
        st.markdown(f"Session ID: `{thread_id}`  Timestamp: {now}")
