"""Data analysis tool for extracting numbers, creating tables, and generating charts."""
from typing import Dict, Any, List, Optional
import re
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import config
from backend.utils.validators import extract_numbers


class DataAnalysisTool:
    """Tool for analyzing numeric data and creating visualizations."""
    
    def __init__(self):
        """Initialize data analysis tool."""
        self.chart_dir = Path(config.CACHE_DIR) / "charts"
        self.chart_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_data(self, text: str) -> Dict[str, Any]:
        """Extract numeric data from text.
        
        Args:
            text: Text containing numbers
            
        Returns:
            Dictionary with extracted numbers and basic statistics
        """
        numbers = extract_numbers(text)
        
        if not numbers:
            return {
                'numbers': [],
                'count': 0,
                'statistics': {}
            }
        
        numbers_array = np.array(numbers)
        
        stats = {
            'count': len(numbers),
            'sum': float(np.sum(numbers_array)),
            'mean': float(np.mean(numbers_array)),
            'median': float(np.median(numbers_array)),
            'min': float(np.min(numbers_array)),
            'max': float(np.max(numbers_array)),
            'std': float(np.std(numbers_array)) if len(numbers) > 1 else 0.0
        }
        
        return {
            'numbers': numbers,
            'count': len(numbers),
            'statistics': stats
        }
    
    def create_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a data table from structured data.
        
        Args:
            data: List of dictionaries with data
            columns: Column names. If None, uses keys from first item
            
        Returns:
            Dictionary with table data in markdown format
        """
        if not data:
            return {
                'table': '',
                'markdown': '',
                'rows': 0,
                'columns': 0
            }
        
        try:
            df = pd.DataFrame(data)
            
            if columns:
                df = df[columns]
            
            # Generate markdown table
            markdown = df.to_markdown(index=False)
            
            return {
                'table': df.to_dict('records'),
                'markdown': markdown,
                'rows': len(df),
                'columns': len(df.columns),
                'columns_list': list(df.columns)
            }
        except Exception as e:
            return {
                'table': '',
                'markdown': '',
                'rows': 0,
                'columns': 0,
                'error': str(e)
            }
    
    def create_chart(
        self,
        data: Dict[str, Any],
        chart_type: str = "bar",
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a chart from data.
        
        Args:
            data: Data dictionary (can be list of numbers, dict with x/y, etc.)
            chart_type: Type of chart ('bar', 'line', 'pie')
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            Dictionary with chart file path and metadata
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Handle different data formats
            if isinstance(data, list):
                # Simple list of numbers
                y_data = data
                x_data = list(range(len(y_data)))
            elif isinstance(data, dict):
                if 'x' in data and 'y' in data:
                    x_data = data['x']
                    y_data = data['y']
                elif 'values' in data:
                    y_data = data['values']
                    x_data = data.get('labels', list(range(len(y_data))))
                else:
                    # Use dict keys and values
                    x_data = list(data.keys())
                    y_data = list(data.values())
            else:
                return {
                    'success': False,
                    'error': 'Unsupported data format'
                }
            
            # Create chart based on type
            if chart_type == 'bar':
                ax.bar(x_data, y_data)
            elif chart_type == 'line':
                ax.plot(x_data, y_data, marker='o')
            elif chart_type == 'pie':
                ax.pie(y_data, labels=x_data, autopct='%1.1f%%')
            else:
                return {
                    'success': False,
                    'error': f'Unsupported chart type: {chart_type}'
                }
            
            # Set labels and title
            if title:
                ax.set_title(title)
            if x_label:
                ax.set_xlabel(x_label)
            if y_label:
                ax.set_ylabel(y_label)
            
            plt.tight_layout()
            
            # Save chart
            import hashlib
            chart_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
            chart_path = self.chart_dir / f"chart_{chart_hash}.{config.CHART_FORMAT}"
            plt.savefig(chart_path, format=config.CHART_FORMAT, dpi=150)
            plt.close()
            
            return {
                'success': True,
                'path': str(chart_path),
                'type': chart_type,
                'title': title
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze(
        self,
        text: Optional[str] = None,
        data: Optional[List[Dict[str, Any]]] = None,
        create_chart: bool = False
    ) -> Dict[str, Any]:
        """Comprehensive data analysis.
        
        Args:
            text: Text to extract numbers from
            data: Structured data for table creation
            create_chart: Whether to create a chart
            
        Returns:
            Dictionary with analysis results
        """
        result = {}
        
        # Extract numbers from text
        if text:
            extracted = self.extract_data(text)
            result['extracted_data'] = extracted
            
            # Create chart if requested and we have numbers
            if create_chart and extracted['numbers']:
                chart = self.create_chart(
                    extracted['numbers'],
                    chart_type='bar',
                    title='Extracted Numbers'
                )
                result['chart'] = chart
        
        # Create table from structured data
        if data:
            table = self.create_table(data)
            result['table'] = table
        
        return result

