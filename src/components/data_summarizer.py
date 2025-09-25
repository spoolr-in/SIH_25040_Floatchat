"""
Data Summarizer Module for FloatChat
Generates intelligent summaries of query results and visualizations.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataSummarizer:
    """Generates intelligent summaries of oceanographic data analysis"""
    
    def __init__(self, interpreter=None):
        """Initialize with optional LLM interpreter for enhanced summaries"""
        self.interpreter = interpreter
        
        # Parameter information for context
        self.parameter_info = {
            'temperature': {
                'unit': '°C',
                'name': 'Temperature',
                'normal_range': (0, 30),
                'description': 'ocean temperature'
            },
            'salinity': {
                'unit': 'PSU',
                'name': 'Salinity', 
                'normal_range': (30, 40),
                'description': 'ocean salinity'
            },
            'pressure': {
                'unit': 'dbar',
                'name': 'Pressure',
                'normal_range': (0, 2000),
                'description': 'water pressure (depth)'
            }
        }
        
        # Location context
        self.location_context = {
            'arabian sea': 'a marginal sea of the northern Indian Ocean',
            'bay of bengal': 'the northeastern part of the Indian Ocean',
            'indian ocean': 'the third-largest ocean covering about 20% of Earth\'s water surface',
            'madagascar': 'the area around the large island nation off the east coast of Africa',
            'maldives': 'the tropical archipelago in the Indian Ocean',
            'sri lanka': 'the waters around the island nation south of India'
        }
    
    def generate_summary(self, results_df: pd.DataFrame, entities, query_text: str, stats: Dict = None) -> str:
        """
        Generate a comprehensive summary of the query results.
        
        Args:
            results_df: Filtered data from the query
            entities: Extracted query entities
            query_text: Original user query
            stats: Statistical summary from visualizer
            
        Returns:
            Human-readable summary string
        """
        if results_df.empty:
            return self._generate_empty_summary(entities)
        
        try:
            # Generate rule-based analysis first (as fallback)
            rule_summary = self._generate_rule_based_summary(results_df, entities, stats)
            
            # Try to enhance with LLM if available
            if self.interpreter:
                try:
                    logger.info("Attempting LLM enhancement for summary")
                    enhanced_summary = self._enhance_with_llm(rule_summary, results_df, entities)
                    
                    # Check if LLM actually provided enhancement
                    if enhanced_summary and enhanced_summary != rule_summary and len(enhanced_summary) > 50:
                        logger.info("Using LLM-enhanced summary")
                        return f"🤖 {enhanced_summary}"  # Add emoji to identify LLM summaries
                    else:
                        logger.warning("LLM enhancement failed or returned insufficient content")
                        
                except Exception as e:
                    logger.warning(f"LLM enhancement failed: {str(e)}")
            
            logger.info("Using rule-based summary")
            return f"📊 {rule_summary}"  # Add emoji to identify rule-based summaries
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return "Unable to generate summary for this query."
    
    def _generate_rule_based_summary(self, df: pd.DataFrame, entities, stats: Dict = None) -> str:
        """Generate summary using rule-based analysis with bullet point formatting"""
        
        summary_parts = []
        
        # Header with better formatting
        summary_parts.append("### 🌊 Ocean Data Analysis Summary\n")
        
        # Query context 
        query_context = self._get_query_context_natural(entities, len(df))
        summary_parts.append(f"**Query Overview:** {query_context}\n")
        
        # Key findings section with better formatting
        summary_parts.append("### 🔍 Key Findings\n")
        
        # Statistical insights
        if entities.parameter and stats:
            statistical_insights = self._generate_statistical_insights_natural(entities.parameter, stats, df)
            summary_parts.append(f"• {statistical_insights}\n")
        
        # Data coverage analysis
        coverage_analysis = self._analyze_data_coverage_natural(df, entities)
        summary_parts.append(f"• {coverage_analysis}\n")
        
        # Temporal analysis
        temporal_insights = self._analyze_temporal_patterns_natural(df)
        if temporal_insights:
            summary_parts.append(f"• {temporal_insights}\n")
        
        # Spatial analysis
        spatial_insights = self._analyze_spatial_distribution_natural(df, entities.location)
        if spatial_insights:
            summary_parts.append(f"• {spatial_insights}\n")
        
        return "\n".join(summary_parts)
    
    def _get_query_context_natural(self, entities, data_count: int) -> str:
        """Generate professional context for decision-makers"""
        
        if entities.parameter and entities.location:
            param_name = self.parameter_info.get(entities.parameter, {}).get('name', entities.parameter.title())
            location_desc = self.location_context.get(entities.location.lower(), entities.location.title())
            return f"Analysis of {data_count:,} {param_name.lower()} measurements from the ARGO global oceanographic monitoring network in {location_desc}."
        
        elif entities.parameter:
            param_name = self.parameter_info.get(entities.parameter, {}).get('name', entities.parameter.title())
            return f"Comprehensive analysis of {data_count:,} {param_name.lower()} observations collected through the international ARGO float network."
        
        else:
            return f"Analysis of {data_count:,} oceanographic measurements from the ARGO global monitoring system, providing critical data for maritime and environmental decision-making."
    
    def _analyze_data_coverage_natural(self, df: pd.DataFrame, entities) -> str:
        """Analyze data coverage for professional decision-making context"""
        
        date_range = df['date'].max() - df['date'].min()
        years = date_range.days / 365.25
        float_count = df['float_id'].nunique()
        
        # Geographic coverage assessment
        lat_range = df['latitude'].max() - df['latitude'].min()
        lon_range = df['longitude'].max() - df['longitude'].min()
        
        coverage_parts = []
        
        # Temporal coverage with reliability assessment
        if years >= 5:
            coverage_parts.append(f"Data spans {years:.1f} years providing robust long-term trend analysis")
        elif years >= 2:
            coverage_parts.append(f"Dataset covers {years:.1f} years offering reliable seasonal and inter-annual patterns")
        elif years >= 1:
            coverage_parts.append(f"{years:.1f}-year coverage provides seasonal insights but limited for long-term trends")
        else:
            months = date_range.days / 30
            coverage_parts.append(f"{months:.0f}-month dataset offers snapshot conditions but limited temporal context")
        
        # Spatial coverage assessment
        if lat_range > 10 and lon_range > 10:
            coverage_parts.append("across extensive oceanic regions providing comprehensive spatial representation")
        elif lat_range > 5 or lon_range > 5:
            coverage_parts.append("covering substantial geographic area suitable for regional analysis")
        else:
            coverage_parts.append("focused on localized area providing high-resolution regional conditions")
        
        # Data source reliability
        if float_count > 10:
            coverage_parts.append(f"Data quality enhanced by {float_count} independent ARGO floats reducing single-source bias")
        elif float_count > 3:
            coverage_parts.append(f"Good spatial coverage from {float_count} ARGO floats providing cross-validation")
        else:
            coverage_parts.append(f"Limited to {float_count} ARGO float{'s' if float_count > 1 else ''}, requiring cautious interpretation")
        
        return ". ".join(coverage_parts) + "."
    
    def _generate_statistical_insights_natural(self, parameter: str, stats: Dict, df: pd.DataFrame) -> str:
        """Generate professional statistical insights for decision-makers"""
        
        param_info = self.parameter_info.get(parameter, {})
        param_name = param_info.get('name', parameter.title())
        unit = param_info.get('unit', '')
        normal_range = param_info.get('normal_range', (0, 100))
        
        mean_val = stats['mean']
        std_val = stats['std']
        min_val, max_val = stats['min'], stats['max']
        
        insights = []
        
        # Statistical summary with context
        insights.append(f"{param_name} averages {mean_val:.2f}{unit} (±{std_val:.2f} standard deviation), ranging from {min_val:.2f} to {max_val:.2f}{unit}")
        
        # Professional interpretation
        if parameter == 'temperature':
            if mean_val > 25:
                insights.append("indicating warm tropical conditions favorable for marine biodiversity but potentially concerning for coral ecosystems")
            elif mean_val > 15:
                insights.append("representing temperate ocean conditions typical for this region, suitable for diverse marine activities")
            else:
                insights.append("showing cooler conditions that may impact shipping routes and marine ecosystem distribution")
                
            # Variability assessment
            if std_val > 5:
                insights.append(f"High temperature variability ({std_val:.1f}°C) suggests seasonal patterns or diverse water masses requiring adaptive maritime strategies")
                
        elif parameter == 'salinity':
            if mean_val > 36:
                insights.append("indicating high salinity conditions typical of evaporation-dominated regions, affecting marine ecosystems and desalination operations")
            elif mean_val > 34:
                insights.append("showing normal oceanic salinity levels supporting typical marine food chains and shipping operations")
            else:
                insights.append("representing lower salinity, possibly due to freshwater input from rivers or precipitation, impacting local marine environments")
                
        elif parameter == 'pressure':
            depth_range = (min_val * 10, max_val * 10)  # rough depth estimate
            insights.append(f"corresponding to depths of approximately {depth_range[0]:.0f}-{depth_range[1]:.0f} meters, covering {'deep ocean' if depth_range[1] > 1000 else 'coastal to mid-depth'} waters")
        
        return ". ".join(insights) + "."
    
    def _analyze_temporal_patterns_natural(self, df: pd.DataFrame) -> str:
        """Analyze temporal patterns for professional decision-making"""
        
        if len(df) < 50:  # Need sufficient data for pattern analysis
            return None
        
        # Group by month to find seasonal patterns
        df_copy = df.copy()
        df_copy['month'] = df_copy['date'].dt.month
        df_copy['year'] = df_copy['date'].dt.year
        
        monthly_counts = df_copy.groupby('month').size()
        
        if len(monthly_counts) < 3:
            return None
        
        # Identify peak and low activity periods
        peak_months = monthly_counts.nlargest(3).index.tolist()
        low_months = monthly_counts.nsmallest(2).index.tolist()
        
        month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                      5: 'May', 6: 'June', 7: 'July', 8: 'August',
                      9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        
        # Professional seasonal analysis
        seasonal_insights = []
        
        # Determine seasonal patterns with professional implications
        if any(month in [6, 7, 8] for month in peak_months):
            seasonal_insights.append("Peak measurement activity during summer months aligns with increased maritime traffic and optimal research conditions")
        elif any(month in [12, 1, 2] for month in peak_months):
            seasonal_insights.append("Higher data density in winter months likely reflects monsoon-driven ocean mixing and increased float displacement")
        elif any(month in [3, 4, 5] for month in peak_months):
            seasonal_insights.append("Spring measurement concentration suggests seasonal research campaigns and transitional oceanographic conditions")
        elif any(month in [9, 10, 11] for month in peak_months):
            seasonal_insights.append("Autumn data clustering indicates post-monsoon sampling periods and seasonal transition monitoring")
        
        # Data gaps analysis
        if len(low_months) > 0:
            low_month_names = [month_names[m] for m in low_months[:2]]
            seasonal_insights.append(f"Reduced coverage in {' and '.join(low_month_names)} may limit seasonal analysis completeness")
        
        # Multi-year trend assessment if applicable
        if len(df_copy['year'].unique()) > 1:
            yearly_counts = df_copy.groupby('year').size()
            if yearly_counts.std() / yearly_counts.mean() > 0.3:  # High variability
                seasonal_insights.append("Significant inter-annual variability in data collection requires careful trend interpretation")
        
        return ". ".join(seasonal_insights) + "." if seasonal_insights else None
    
    def _analyze_spatial_distribution_natural(self, df: pd.DataFrame, location: str) -> str:
        """Analyze spatial distribution naturally"""
        
        if len(df) < 100:
            return None
        
        # Calculate spatial clustering
        lat_std = df['latitude'].std()
        lon_std = df['longitude'].std()
        
        # Geographic center
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        insights = []
        
        if lat_std < 1 and lon_std < 1:
            insights.append("The measurements are tightly clustered")
        elif lat_std < 5 and lon_std < 5:
            insights.append("Data points are moderately distributed")
        else:
            insights.append("The measurements span a wide geographic area")
        
        # Add location-specific context
        if location:
            if 'arabian' in location.lower():
                insights.append("within the Arabian Sea's unique oceanographic environment")
            elif 'bengal' in location.lower():
                insights.append("across the Bay of Bengal's monsoon-influenced waters")
            elif 'indian' in location.lower():
                insights.append("throughout the Indian Ocean basin")
            elif 'madagascar' in location.lower():
                insights.append("around Madagascar's complex coastal currents")
        
        if center_lat > 0:
            hemisphere = "northern hemisphere waters"
        else:
            hemisphere = "southern hemisphere waters"
        
        insights.append(f"primarily in {hemisphere}")
        
        return ", ".join(insights) + "."
    
    def _get_query_context(self, entities, data_count: int) -> str:
        """Generate context about what was queried"""
        
        if entities.parameter and entities.location:
            param_name = self.parameter_info.get(entities.parameter, {}).get('description', entities.parameter)
            location_desc = self.location_context.get(entities.location.lower(), entities.location)
            return f"**Analysis Overview:** Found {data_count:,} measurements of {param_name} in {location_desc}."
        
        elif entities.parameter:
            param_name = self.parameter_info.get(entities.parameter, {}).get('description', entities.parameter)
            return f"**Analysis Overview:** Found {data_count:,} measurements of {param_name} across the dataset."
        
        elif entities.location:
            location_desc = self.location_context.get(entities.location.lower(), entities.location)
            return f"**Analysis Overview:** Found {data_count:,} oceanographic measurements in {location_desc}."
        
        else:
            return f"**Analysis Overview:** Found {data_count:,} oceanographic measurements in the selected area."
    
    def _analyze_data_coverage(self, df: pd.DataFrame, entities) -> str:
        """Analyze temporal and spatial coverage"""
        
        insights = []
        
        # Temporal coverage
        if 'date' in df.columns:
            date_range = df['date'].max() - df['date'].min()
            start_year = df['date'].min().year
            end_year = df['date'].max().year
            
            if date_range.days > 365:
                insights.append(f"Data spans {date_range.days // 365} years ({start_year}-{end_year})")
            else:
                insights.append(f"Data covers {date_range.days} days in {start_year}")
        
        # Float coverage
        if 'float_id' in df.columns:
            float_count = df['float_id'].nunique()
            if float_count > 1:
                insights.append(f"from {float_count} different ARGO floats")
            else:
                insights.append(f"from 1 ARGO float")
        
        # Depth coverage
        if 'pressure' in df.columns:
            max_depth = df['pressure'].max()
            min_depth = df['pressure'].min()
            if max_depth > 1000:
                insights.append(f"covering depths from {min_depth:.0f} to {max_depth:.0f} dbar (deep ocean)")
            elif max_depth > 200:
                insights.append(f"covering depths from {min_depth:.0f} to {max_depth:.0f} dbar (mid-water)")
            else:
                insights.append(f"covering shallow depths from {min_depth:.0f} to {max_depth:.0f} dbar")
        
        return "**Data Coverage:** " + ", ".join(insights) + "."
    
    def _generate_statistical_insights(self, parameter: str, stats: Dict, df: pd.DataFrame) -> str:
        """Generate insights about parameter statistics"""
        
        param_info = self.parameter_info.get(parameter, {})
        param_name = param_info.get('name', parameter)
        unit = param_info.get('unit', '')
        normal_range = param_info.get('normal_range', (None, None))
        
        insights = []
        
        # Basic statistics
        mean_val = stats.get('mean', 0)
        std_val = stats.get('std', 0)
        min_val = stats.get('min', 0)
        max_val = stats.get('max', 0)
        
        insights.append(f"**{param_name} Analysis:** Average value is {mean_val:.1f}{unit}")
        
        # Variability assessment
        if std_val / mean_val > 0.2:  # High variability
            insights.append(f"with high variability (σ={std_val:.1f}{unit})")
        elif std_val / mean_val > 0.1:  # Moderate variability
            insights.append(f"with moderate variability (σ={std_val:.1f}{unit})")
        else:
            insights.append(f"with low variability (σ={std_val:.1f}{unit})")
        
        # Range assessment
        range_val = max_val - min_val
        insights.append(f"Values range from {min_val:.1f} to {max_val:.1f}{unit}")
        
        # Comparison to normal ranges
        if normal_range[0] is not None and normal_range[1] is not None:
            if min_val < normal_range[0] or max_val > normal_range[1]:
                insights.append("including some extreme values")
            elif mean_val < normal_range[0]:
                insights.append("showing generally low values")
            elif mean_val > normal_range[1]:
                insights.append("showing generally high values")
            else:
                insights.append("within typical oceanic ranges")
        
        return " ".join(insights) + "."
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Optional[str]:
        """Analyze temporal patterns in the data"""
        
        if 'date' not in df.columns or len(df) < 10:
            return None
        
        insights = []
        
        # Seasonal analysis
        df_copy = df.copy()
        df_copy['month'] = df_copy['date'].dt.month
        monthly_counts = df_copy.groupby('month').size()
        
        if len(monthly_counts) > 6:  # Multi-seasonal data
            peak_month = monthly_counts.idxmax()
            peak_season = self._get_season_name(peak_month)
            insights.append(f"Most measurements collected during {peak_season}")
        
        # Temporal distribution
        date_span = df['date'].max() - df['date'].min()
        total_days = date_span.days
        measurement_frequency = len(df) / max(total_days, 1)
        
        if measurement_frequency > 1:
            insights.append(f"with frequent sampling (avg {measurement_frequency:.1f} measurements/day)")
        elif measurement_frequency > 0.1:
            insights.append("with regular sampling intervals")
        else:
            insights.append("with sparse temporal coverage")
        
        if insights:
            return "**Temporal Patterns:** " + ", ".join(insights) + "."
        return None
    
    def _analyze_spatial_distribution(self, df: pd.DataFrame, location: str = None) -> Optional[str]:
        """Analyze spatial distribution patterns"""
        
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            return None
        
        insights = []
        
        # Geographic spread
        lat_range = df['latitude'].max() - df['latitude'].min()
        lon_range = df['longitude'].max() - df['longitude'].min()
        
        if lat_range > 10 or lon_range > 10:
            insights.append("widely distributed across the region")
        elif lat_range > 2 or lon_range > 2:
            insights.append("moderately spread across the area")
        else:
            insights.append("concentrated in a specific area")
        
        # Coordinate ranges for context
        lat_center = df['latitude'].mean()
        lon_center = df['longitude'].mean()
        
        if lat_center > 0:
            hemisphere = "Northern Hemisphere"
        else:
            hemisphere = "Southern Hemisphere"
            
        insights.append(f"centered around {abs(lat_center):.1f}°{'N' if lat_center > 0 else 'S'}, {abs(lon_center):.1f}°{'E' if lon_center > 0 else 'W'}")
        
        return "**Spatial Distribution:** " + ", ".join(insights) + "."
    
    def _assess_data_quality(self, df: pd.DataFrame, entities) -> str:
        """Assess data quality and completeness"""
        
        insights = []
        
        # Completeness assessment
        total_records = len(df)
        
        if entities.parameter:
            valid_param = df[entities.parameter].notna().sum()
            completeness = (valid_param / total_records) * 100
            
            if completeness > 95:
                insights.append("excellent data quality")
            elif completeness > 85:
                insights.append("good data quality")
            else:
                insights.append(f"moderate data quality ({completeness:.0f}% complete)")
        
        # Location data quality
        if 'latitude' in df.columns and 'longitude' in df.columns:
            valid_coords = df[['latitude', 'longitude']].notna().all(axis=1).sum()
            coord_completeness = (valid_coords / total_records) * 100
            
            if coord_completeness < 90:
                insights.append(f"some location data missing ({coord_completeness:.0f}% with coordinates)")
        
        return "**Data Quality:** " + ", ".join(insights) + "."
    
    def _get_season_name(self, month: int) -> str:
        """Convert month number to season name"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _generate_empty_summary(self, entities) -> str:
        """Generate summary for empty results"""
        
        if entities.location and entities.parameter:
            return f"**No Data Found:** No {entities.parameter} measurements were found in the specified location ({entities.location}). Try expanding your search area or checking different time periods."
        
        elif entities.parameter:
            return f"**No Data Found:** No {entities.parameter} measurements match your query criteria. The dataset may not contain this parameter or the filters are too restrictive."
        
        elif entities.location:
            return f"**No Data Found:** No measurements were found in {entities.location}. This location may be outside our dataset coverage area."
        
        else:
            return "**No Data Found:** Your query didn't match any data in the dataset. Please try different search terms or broaden your criteria."
    
    def _enhance_with_llm(self, rule_summary: str, df: pd.DataFrame, entities) -> str:
        """Enhance rule-based summary with LLM natural language generation"""
        
        try:
            # Create a comprehensive, decision-oriented prompt for LLM
            avg_value = "N/A"
            if entities.parameter and entities.parameter in df.columns:
                avg_value = f"{df[entities.parameter].mean():.1f}"
            
            prompt = f"""Write a comprehensive summary of ocean data analysis for government officials, environmental policymakers, and maritime industry professionals:

Dataset: {len(df):,} measurements from ARGO oceanographic monitoring network
Parameter: {entities.parameter or 'Ocean conditions'}  
Location: {entities.location or 'Global coverage'}
Average value: {avg_value}

Format your response EXACTLY as shown below with proper line breaks:

### 🔍 Key Findings

• [First main finding with specific data]

• [Second main finding with measurements] 

• [Third finding with trends/patterns]


### 📊 Data Assessment

• [Geographic coverage details]

• [Temporal coverage information]

• [Data quality indicators]


### 💡 Implications & Insights  

• [Environmental impact assessment]

• [Maritime operational considerations]

• [Policy recommendations]


Each bullet point MUST be on a separate line. Use specific numbers and technical details. Write professionally for decision-makers."""

            # Check if we have LLM capability through the interpreter
            if hasattr(self.interpreter, 'test_connection') and self.interpreter.test_connection():
                # Try to get LLM response using Ollama API directly
                try:
                    import requests
                    
                    response = requests.post('http://localhost:11434/api/generate', 
                        json={
                            'model': 'gemma2:2b',
                            'prompt': prompt,
                            'stream': False
                        }, 
                        timeout=8  # Increased timeout for more reliable LLM responses
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        enhanced_text = result.get('response', '').strip()
                        
                        if enhanced_text and len(enhanced_text) > 50:  # Valid response
                            return enhanced_text
                        
                except Exception as llm_error:
                    logger.debug(f"LLM API call failed: {llm_error}")
            
            # Fallback: return rule-based summary
            return rule_summary
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}")
            return rule_summary
