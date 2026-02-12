import sys
import io
import logging
import traceback
from typing import Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

logger = logging.getLogger(__name__)


class PythonREPL:
    """
    Safe Python REPL for executing data analysis code.
    Restricted to pandas, plotly, and numpy operations.
    """
    
    def __init__(self, dataframe: Optional[pd.DataFrame] = None, save_callback: Optional[callable] = None):
        """
        Initialize REPL with a dataframe.
        
        Args:
            dataframe: Pandas DataFrame to make available as 'df'
            save_callback: Optional callback for global plot registration
        """
        self.dataframe = dataframe
        self.save_callback = save_callback
        self.plots: Dict[str, go.Figure] = {}
        self.namespace = {
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'df': dataframe,
            'save_plot': self._save_plot,
            'print': print
        }
    
    def _save_plot(self, plot_id: str, fig: go.Figure):
        """
        Save a plot for later retrieval.
        
        Args:
            plot_id: Unique identifier for the plot
            fig: Plotly figure object
        """
        logger.info(f"Saving plot with ID: {plot_id}")
        self.plots[plot_id] = fig
        if self.save_callback:
            self.save_callback(plot_id, fig)
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code and capture output.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict with 'success', 'output', 'error', and 'plots' keys
        """
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        result = {
            'success': False,
            'output': '',
            'error': None,
            'plots': []
        }
        
        try:
            # Update dataframe in namespace if it changed
            self.namespace['df'] = self.dataframe
            
            # Execute code
            exec(code, self.namespace)
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Check if there's a result variable
            if 'result' in self.namespace:
                output += str(self.namespace['result'])
            
            result['success'] = True
            result['output'] = output.strip()
            result['plots'] = list(self.plots.keys())
            
        except Exception as e:
            result['error'] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        return result
    
    def get_plot(self, plot_id: str) -> Optional[go.Figure]:
        """
        Retrieve a saved plot.
        
        Args:
            plot_id: Plot identifier
            
        Returns:
            Plotly figure or None
        """
        return self.plots.get(plot_id)
    
    def clear_plots(self):
        """Clear all saved plots."""
        self.plots.clear()
    
    def update_dataframe(self, dataframe: pd.DataFrame):
        """
        Update the dataframe available in the REPL.
        
        Args:
            dataframe: New dataframe
        """
        self.dataframe = dataframe
        self.namespace['df'] = dataframe
