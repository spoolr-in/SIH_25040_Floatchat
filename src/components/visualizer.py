"""
Visualizer Module for FloatChat
Creates interactive Plotly visualizations for ocean data.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class DataVisualizer:
    """Creates interactive visualizations for oceanographic data"""
    
    def __init__(self):
        """Initialize the visualizer"""
        # Color scales for different parameters
        self.color_scales = {
            'temperature': 'RdYlBu_r',  # Red-Yellow-Blue (reversed)
            'salinity': 'Viridis',      # Green-Blue-Purple
            'pressure': 'Blues',        # Blue gradient
            'default': 'Viridis'
        }
        
        # Parameter units and descriptions
        self.parameter_info = {
            'temperature': {'unit': '°C', 'name': 'Temperature'},
            'salinity': {'unit': 'PSU', 'name': 'Salinity'},
            'pressure': {'unit': 'dbar', 'name': 'Pressure'},
        }
    
    def create_map_visualization(self, 
                                df: pd.DataFrame, 
                                parameter: str = None,
                                title: str = None) -> go.Figure:
        """
        Create an interactive map visualization.
        
        Args:
            df: DataFrame with oceanographic data
            parameter: Parameter to visualize (temperature, salinity, pressure)
            title: Custom title for the plot
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_map("No data found for the requested query")
        
        # Validate required columns
        required_cols = ['latitude', 'longitude']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return self._create_empty_map(f"Missing required columns: {missing_cols}")
        
        try:
            # Prepare data for plotting
            plot_df = df.copy()
            
            # Set up parameter-specific configurations
            if parameter and parameter in plot_df.columns:
                # Remove rows with missing parameter values
                plot_df = plot_df.dropna(subset=[parameter])
                
                if plot_df.empty:
                    return self._create_empty_map(f"No valid {parameter} data found")
                
                color_col = parameter
                color_scale = self.color_scales.get(parameter, self.color_scales['default'])
                param_info = self.parameter_info.get(parameter, {'unit': '', 'name': parameter})
                
                hover_template = (
                    f"<b>Location:</b> (%{{lat:.2f}}, %{{lon:.2f}})<br>"
                    f"<b>{param_info['name']}:</b> %{{customdata[0]:.2f}} {param_info['unit']}<br>"
                    f"<b>Date:</b> %{{customdata[1]}}<br>"
                    f"<b>Float ID:</b> %{{customdata[2]}}<br>"
                    "<extra></extra>"
                )
                
                # Prepare custom data for hover
                custom_data = np.column_stack([
                    plot_df[parameter],
                    plot_df['date'].dt.strftime('%Y-%m-%d') if 'date' in plot_df.columns else ['N/A'] * len(plot_df),
                    plot_df['float_id'] if 'float_id' in plot_df.columns else ['N/A'] * len(plot_df)
                ])
                
            else:
                # No parameter specified, show all points
                color_col = None
                color_scale = None
                hover_template = (
                    f"<b>Location:</b> (%{{lat:.2f}}, %{{lon:.2f}})<br>"
                    f"<b>Date:</b> %{{customdata[0]}}<br>"
                    f"<b>Float ID:</b> %{{customdata[1]}}<br>"
                    "<extra></extra>"
                )
                
                custom_data = np.column_stack([
                    plot_df['date'].dt.strftime('%Y-%m-%d') if 'date' in plot_df.columns else ['N/A'] * len(plot_df),
                    plot_df['float_id'] if 'float_id' in plot_df.columns else ['N/A'] * len(plot_df)
                ])
            
            # Sample data if too large (for performance)
            if len(plot_df) > 5000:
                logger.info(f"Sampling {len(plot_df)} points down to 5000 for visualization")
                plot_df = plot_df.sample(n=5000).copy()
                custom_data = custom_data[:5000] if len(custom_data) > 5000 else custom_data
            
            # Create the map
            fig = px.scatter_mapbox(
                plot_df,
                lat='latitude',
                lon='longitude',
                color=color_col,
                color_continuous_scale=color_scale,
                size_max=15,
                zoom=3,
                mapbox_style="open-street-map",
                title=title or self._generate_title(parameter, len(plot_df)),
                height=600
            )
            
            # Update traces with custom hover template
            fig.update_traces(
                customdata=custom_data,
                hovertemplate=hover_template
            )
            
            # Update layout
            fig.update_layout(
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                showlegend=True if parameter else False,
                coloraxis_colorbar=dict(
                    title=f"{self.parameter_info.get(parameter, {}).get('name', parameter)} "
                          f"({self.parameter_info.get(parameter, {}).get('unit', '')})"
                ) if parameter else None
            )
            
            # Set initial map center based on data
            center_lat = plot_df['latitude'].mean()
            center_lon = plot_df['longitude'].mean()
            fig.update_layout(
                mapbox=dict(
                    center=dict(lat=center_lat, lon=center_lon)
                )
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create map visualization: {str(e)}")
            return self._create_empty_map(f"Visualization error: {str(e)}")
    
    def create_time_series(self, df: pd.DataFrame, parameter: str) -> go.Figure:
        """
        Create a time series plot for a parameter.
        
        Args:
            df: DataFrame with oceanographic data
            parameter: Parameter to plot over time
            
        Returns:
            Plotly Figure object
        """
        if df.empty or parameter not in df.columns or 'date' not in df.columns:
            return self._create_empty_plot("No valid time series data available")
        
        try:
            # Prepare data
            plot_df = df.dropna(subset=[parameter, 'date']).copy()
            plot_df = plot_df.sort_values('date')
            
            # Group by float_id if available
            if 'float_id' in plot_df.columns:
                fig = px.line(
                    plot_df, 
                    x='date', 
                    y=parameter,
                    color='float_id',
                    title=f"{self.parameter_info.get(parameter, {}).get('name', parameter)} Over Time",
                    labels={
                        parameter: f"{self.parameter_info.get(parameter, {}).get('name', parameter)} "
                                  f"({self.parameter_info.get(parameter, {}).get('unit', '')})",
                        'date': 'Date'
                    }
                )
            else:
                fig = px.line(
                    plot_df, 
                    x='date', 
                    y=parameter,
                    title=f"{self.parameter_info.get(parameter, {}).get('name', parameter)} Over Time"
                )
            
            fig.update_layout(height=400)
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create time series: {str(e)}")
            return self._create_empty_plot(f"Time series error: {str(e)}")
    
    def create_depth_profile(self, df: pd.DataFrame, parameter: str) -> go.Figure:
        """
        Create a depth profile plot.
        
        Args:
            df: DataFrame with oceanographic data
            parameter: Parameter to plot against depth
            
        Returns:
            Plotly Figure object
        """
        if df.empty or parameter not in df.columns or 'pressure' not in df.columns:
            return self._create_empty_plot("No valid depth profile data available")
        
        try:
            plot_df = df.dropna(subset=[parameter, 'pressure']).copy()
            
            fig = px.scatter(
                plot_df,
                x=parameter,
                y='pressure',
                color='float_id' if 'float_id' in plot_df.columns else None,
                title=f"{self.parameter_info.get(parameter, {}).get('name', parameter)} Depth Profile",
                labels={
                    parameter: f"{self.parameter_info.get(parameter, {}).get('name', parameter)} "
                              f"({self.parameter_info.get(parameter, {}).get('unit', '')})",
                    'pressure': 'Depth (dbar)'
                }
            )
            
            # Invert y-axis (depth increases downward)
            fig.update_layout(yaxis=dict(autorange="reversed"))
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create depth profile: {str(e)}")
            return self._create_empty_plot(f"Depth profile error: {str(e)}")
    
    def _create_empty_map(self, message: str) -> go.Figure:
        """Create an empty map with a message"""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=message,
            showarrow=False,
            font=dict(size=16),
            xref="paper", yref="paper"
        )
        fig.update_layout(
            title="Ocean Data Visualization",
            height=600,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def _create_empty_plot(self, message: str) -> go.Figure:
        """Create an empty plot with a message"""
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=message,
            showarrow=False,
            font=dict(size=14),
            xref="paper", yref="paper"
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def _generate_title(self, parameter: str = None, count: int = 0) -> str:
        """Generate an appropriate title for the visualization"""
        if parameter:
            param_name = self.parameter_info.get(parameter, {}).get('name', parameter)
            return f"{param_name} Distribution ({count:,} measurements)"
        else:
            return f"Ocean Float Data Locations ({count:,} points)"
    
    def get_summary_stats(self, df: pd.DataFrame, parameter: str) -> Dict[str, Any]:
        """Get summary statistics for a parameter"""
        if df.empty or parameter not in df.columns:
            return {}
        
        try:
            data = df[parameter].dropna()
            if data.empty:
                return {}
            
            return {
                'count': len(data),
                'mean': float(data.mean()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'median': float(data.median()),
                'unit': self.parameter_info.get(parameter, {}).get('unit', '')
            }
        except Exception as e:
            logger.error(f"Failed to compute summary statistics: {str(e)}")
            return {}
