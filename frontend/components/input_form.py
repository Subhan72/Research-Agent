"""Streamlit component for research query input."""
import streamlit as st


def render_input_form():
    """Render the research query input form.
    
    Returns:
        Tuple of (query, generate_pdf, use_cache) if submitted, else (None, False, True)
    """
    st.header("🔍 AI Research Assistant")
    st.markdown("Enter your research topic or question below:")
    
    query = st.text_area(
        "Research Query",
        height=100,
        placeholder="e.g., Impact of AI on Pakistani job market",
        key="research_query"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        generate_pdf = st.checkbox("Generate PDF Report", value=False)
    
    with col2:
        use_cache = st.checkbox("Use Cache", value=True)
    
    submitted = st.button("Start Research", type="primary", use_container_width=True)
    
    if submitted and query:
        return query.strip(), generate_pdf, use_cache
    elif submitted and not query:
        st.warning("Please enter a research query.")
        return None, False, True
    
    return None, False, True

