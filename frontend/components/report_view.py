"""Streamlit component for displaying and downloading research reports."""
import streamlit as st
from typing import Dict, Any
from pathlib import Path


def render_report(report_data: Dict[str, Any]):
    """Render the research report.
    
    Args:
        report_data: Report data dictionary with markdown and metadata
    """
    if not report_data:
        st.warning("No report data available.")
        return
    
    markdown = report_data.get('markdown', '')
    citations = report_data.get('citations', [])
    
    if markdown:
        st.markdown("---")
        st.header("📄 Research Report")
        
        # Display markdown report
        st.markdown(markdown, unsafe_allow_html=False)
        
        # Display citations if not already in markdown
        if citations and "## References" not in markdown:
            st.markdown("---")
            st.subheader("References")
            for i, citation in enumerate(citations, 1):
                st.markdown(f"{i}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})")
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Markdown",
                data=markdown,
                file_name="research_report.md",
                mime="text/markdown"
            )
        
        with col2:
            # PDF download will be handled separately if PDF was generated
            if 'pdf_path' in report_data:
                pdf_path = report_data.get('pdf_path')
                if Path(pdf_path).exists():
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download PDF",
                            data=f.read(),
                            file_name="research_report.pdf",
                            mime="application/pdf"
                        )

