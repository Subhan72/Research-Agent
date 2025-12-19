"""Streamlit component for displaying research progress."""
import streamlit as st
from typing import Dict, Any


def render_progress(step: str, status: str):
    """Render progress indicator.
    
    Args:
        step: Current step name
        status: Step status ('in_progress', 'completed', 'pending')
    """
    steps = ['planning', 'execution', 'synthesis', 'complete']
    
    # Create progress bar
    current_index = steps.index(step) if step in steps else 0
    progress = (current_index + 1) / len(steps)
    
    st.progress(progress)
    
    # Display step status
    status_icons = {
        'in_progress': '⏳',
        'completed': '✅',
        'pending': '⏸️'
    }
    
    icon = status_icons.get(status, '⏸️')
    st.caption(f"{icon} {step.replace('_', ' ').title()}: {status.replace('_', ' ').title()}")

