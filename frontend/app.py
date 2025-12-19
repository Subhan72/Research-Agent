"""Streamlit frontend for AI Research Assistant."""
import streamlit as st
import requests
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from frontend.components.input_form import render_input_form
from frontend.components.progress_view import render_progress
from frontend.components.report_view import render_report

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'pending'
if 'tool_results' not in st.session_state:
    st.session_state.tool_results = []


def call_research_api(query: str, generate_pdf: bool, use_cache: bool) -> Optional[Dict[str, Any]]:
    """Call the research API and handle streaming responses.
    
    Args:
        query: Research query
        generate_pdf: Whether to generate PDF
        use_cache: Whether to use cache
        
    Returns:
        Complete research results or None on error
    """
    try:
        # Use sync endpoint for simplicity (can be changed to streaming)
        response = requests.post(
            f"{API_URL}/agent/research/sync",
            json={
                "query": query,
                "generate_pdf": generate_pdf,
                "use_cache": use_cache
            },
            timeout=600  # 10 minute timeout
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to API. Make sure the backend server is running on port 8000.")
        st.info("Start the backend with: `uvicorn backend.main:app --reload`")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The research is taking too long.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def display_tool_results(tool_results: list):
    """Display expandable sections for each tool result.
    
    Args:
        tool_results: List of tool execution results
    """
    if not tool_results:
        return
    
    st.markdown("---")
    st.subheader("🔧 Tool Results")
    
    for i, result in enumerate(tool_results):
        tool_name = result.get('tool', 'unknown')
        success = result.get('success', False)
        
        with st.expander(f"{'✅' if success else '❌'} {tool_name.replace('_', ' ').title()}", expanded=False):
            if success:
                tool_data = result.get('result', {})
                st.json(tool_data)
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")


def main():
    """Main application function."""
    # Render input form
    query, generate_pdf, use_cache = render_input_form()
    
    # Handle research request
    if query:
        with st.spinner("Conducting research..."):
            results = call_research_api(query, generate_pdf, use_cache)
            
            if results:
                st.session_state.research_results = results
                
                # Display plan
                plan = results.get('plan', {})
                if plan:
                    st.markdown("---")
                    st.subheader("📋 Research Plan")
                    
                    sub_questions = plan.get('sub_questions', [])
                    if sub_questions:
                        st.markdown("**Sub-questions:**")
                        for i, question in enumerate(sub_questions, 1):
                            st.markdown(f"{i}. {question}")
                    
                    tool_sequence = plan.get('tool_sequence', [])
                    if tool_sequence:
                        st.markdown(f"**Tool Sequence:** {', '.join(tool_sequence)}")
                    
                    reasoning = plan.get('reasoning', '')
                    if reasoning:
                        st.info(f"💡 {reasoning}")
                
                # Display tool results
                tool_results = results.get('tool_results', [])
                if tool_results:
                    display_tool_results(tool_results)
                    st.session_state.tool_results = tool_results
                
                # Display report
                report = results.get('report', {})
                if report:
                    # Add PDF path if available
                    pdf_result = results.get('pdf', {})
                    if pdf_result and pdf_result.get('success'):
                        report['pdf_path'] = pdf_result.get('path')
                    
                    render_report(report)
    
    # Display previous results if available
    elif st.session_state.research_results:
        st.info("💡 Enter a new query to start another research session.")
        
        if st.button("Clear Previous Results"):
            st.session_state.research_results = None
            st.session_state.tool_results = []
            st.rerun()


if __name__ == "__main__":
    main()

