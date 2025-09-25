"""
Query Engine for FloatChat
Handles data filtering, geocoding, and location-based queries.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QueryEngine:
    """Data filtering and query processing engine"""
    
    def __init__(self, data_path: str):
        """
        Initialize the query engine with the master dataset.
        
        Args:
            data_path: Path to the master_dataset.parquet file
        """
        self.data_path = data_path
        self.data = None
        self.geocoder = Nominatim(user_agent="floatchat-v1.0")
        
        # Predefined bounding boxes for common ocean regions
        self.location_bounds = {
            'arabian sea': {'lat_min': 10, 'lat_max': 25, 'lon_min': 50, 'lon_max': 80},
            'bay of bengal': {'lat_min': 5, 'lat_max': 22, 'lon_min': 80, 'lon_max': 100},
            'indian ocean': {'lat_min': -50, 'lat_max': 30, 'lon_min': 20, 'lon_max': 147},
            'equatorial indian ocean': {'lat_min': -10, 'lat_max': 10, 'lon_min': 40, 'lon_max': 100},
            'southern ocean': {'lat_min': -70, 'lat_max': -40, 'lon_min': -180, 'lon_max': 180},
            'madagascar': {'lat_min': -26, 'lat_max': -11, 'lon_min': 43, 'lon_max': 51},
            'maldives': {'lat_min': -1, 'lat_max': 8, 'lon_min': 72, 'lon_max': 74},
            'sri lanka': {'lat_min': 5, 'lat_max': 10, 'lon_min': 79, 'lon_max': 82},
        }
        
        self.load_data()
    
    def load_data(self):
        """Load the master dataset"""
        try:
            self.data = pd.read_parquet(self.data_path)
            logger.info(f"Loaded dataset with {len(self.data)} records")
            
            # Ensure date column is datetime
            if 'date' in self.data.columns:
                self.data['date'] = pd.to_datetime(self.data['date'])
            
        except Exception as e:
            logger.error(f"Failed to load data from {self.data_path}: {str(e)}")
            raise
    
    def get_location_bounds(self, location: str) -> Optional[Dict[str, float]]:
        """
        Get bounding box coordinates for a location.
        
        Args:
            location: Location name
            
        Returns:
            Dictionary with lat_min, lat_max, lon_min, lon_max or None
        """
        location_lower = location.lower()
        
        # Check predefined locations first
        if location_lower in self.location_bounds:
            return self.location_bounds[location_lower]
        
        # Try geocoding for dynamic location lookup
        try:
            logger.info(f"Geocoding location: {location}")
            location_data = self.geocoder.geocode(location, exactly_one=True, timeout=10)
            
            if location_data:
                lat, lon = location_data.latitude, location_data.longitude
                
                # Create a bounding box around the point (±2 degrees)
                bounds = {
                    'lat_min': lat - 2,
                    'lat_max': lat + 2,
                    'lon_min': lon - 2,
                    'lon_max': lon + 2
                }
                
                logger.info(f"Geocoded {location} to bounds: {bounds}")
                return bounds
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding failed for {location}: {str(e)}")
        
        return None
    
    def filter_by_location(self, df: pd.DataFrame, location: str) -> pd.DataFrame:
        """
        Filter data by geographic location.
        
        Args:
            df: DataFrame to filter
            location: Location name
            
        Returns:
            Filtered DataFrame
        """
        bounds = self.get_location_bounds(location)
        
        if bounds is None:
            logger.warning(f"Could not find bounds for location: {location}")
            return df  # Return unfiltered data if location not found
        
        # Apply geographic filter
        mask = (
            (df['latitude'] >= bounds['lat_min']) &
            (df['latitude'] <= bounds['lat_max']) &
            (df['longitude'] >= bounds['lon_min']) &
            (df['longitude'] <= bounds['lon_max'])
        )
        
        filtered_df = df[mask]
        logger.info(f"Location filter '{location}' reduced data from {len(df)} to {len(filtered_df)} records")
        
        return filtered_df
    
    def filter_by_parameter(self, df: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """
        Filter data by parameter availability.
        
        Args:
            df: DataFrame to filter
            parameter: Parameter name (temperature, salinity, pressure)
            
        Returns:
            Filtered DataFrame
        """
        if parameter not in df.columns:
            logger.warning(f"Parameter '{parameter}' not found in dataset")
            return df
        
        # Remove rows where the parameter is null
        filtered_df = df.dropna(subset=[parameter])
        logger.info(f"Parameter filter '{parameter}' reduced data from {len(df)} to {len(filtered_df)} records")
        
        return filtered_df
    
    def filter_by_date(self, df: pd.DataFrame, date: str = None, date_range: Dict = None) -> pd.DataFrame:
        """
        Filter data by date or date range.
        
        Args:
            df: DataFrame to filter
            date: Specific date (YYYY-MM-DD)
            date_range: Dict with 'start' and 'end' keys
            
        Returns:
            Filtered DataFrame
        """
        if 'date' not in df.columns:
            logger.warning("No date column found in dataset")
            return df
        
        original_len = len(df)
        
        if date:
            try:
                target_date = pd.to_datetime(date)
                # Filter for data within ±30 days of target date
                start_date = target_date - timedelta(days=30)
                end_date = target_date + timedelta(days=30)
                
                mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                filtered_df = df[mask]
                
                logger.info(f"Date filter '{date}' (±30 days) reduced data from {original_len} to {len(filtered_df)} records")
                return filtered_df
                
            except Exception as e:
                logger.error(f"Failed to parse date '{date}': {str(e)}")
        
        elif date_range:
            try:
                start_date = pd.to_datetime(date_range.get('start'))
                end_date = pd.to_datetime(date_range.get('end'))
                
                mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                filtered_df = df[mask]
                
                logger.info(f"Date range filter reduced data from {original_len} to {len(filtered_df)} records")
                return filtered_df
                
            except Exception as e:
                logger.error(f"Failed to parse date range: {str(e)}")
        
        return df
    
    def filter_by_depth(self, df: pd.DataFrame, depth_range: Dict) -> pd.DataFrame:
        """
        Filter data by depth/pressure range.
        
        Args:
            df: DataFrame to filter
            depth_range: Dict with 'min' and 'max' depth values
            
        Returns:
            Filtered DataFrame
        """
        if 'pressure' not in df.columns:
            logger.warning("No pressure column found for depth filtering")
            return df
        
        try:
            min_depth = depth_range.get('min', 0)
            max_depth = depth_range.get('max', float('inf'))
            
            # Approximate conversion: 1 meter depth ≈ 1 dbar pressure
            mask = (df['pressure'] >= min_depth) & (df['pressure'] <= max_depth)
            filtered_df = df[mask]
            
            logger.info(f"Depth filter ({min_depth}-{max_depth}m) reduced data from {len(df)} to {len(filtered_df)} records")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Failed to apply depth filter: {str(e)}")
            return df
    
    def execute_query(self, entities) -> pd.DataFrame:
        """
        Execute a query based on extracted entities.
        
        Args:
            entities: QueryEntity object with extracted parameters
            
        Returns:
            Filtered DataFrame
        """
        logger.info(f"Executing query with entities: {entities}")
        
        if self.data is None:
            logger.error("No data loaded")
            return pd.DataFrame()
        
        # Start with full dataset
        result_df = self.data.copy()
        
        # Apply filters based on entities
        if entities.parameter:
            result_df = self.filter_by_parameter(result_df, entities.parameter)
        
        if entities.location:
            result_df = self.filter_by_location(result_df, entities.location)
        
        if entities.date:
            result_df = self.filter_by_date(result_df, date=entities.date)
        elif entities.date_range:
            result_df = self.filter_by_date(result_df, date_range=entities.date_range)
        
        if entities.depth_range:
            result_df = self.filter_by_depth(result_df, entities.depth_range)
        
        # Limit results for performance (show latest data first)
        if len(result_df) > 10000:
            logger.info(f"Limiting results from {len(result_df)} to 10000 records")
            result_df = result_df.nlargest(10000, 'date')
        
        logger.info(f"Query executed successfully, returning {len(result_df)} records")
        return result_df
    
    def get_dataset_summary(self) -> Dict:
        """Get summary statistics of the loaded dataset"""
        if self.data is None:
            return {}
        
        return {
            'total_records': len(self.data),
            'float_count': self.data['float_id'].nunique() if 'float_id' in self.data.columns else 0,
            'date_range': {
                'start': self.data['date'].min().isoformat() if 'date' in self.data.columns else None,
                'end': self.data['date'].max().isoformat() if 'date' in self.data.columns else None
            },
            'parameter_counts': {
                param: self.data[param].notna().sum() 
                for param in ['temperature', 'salinity', 'pressure']
                if param in self.data.columns
            },
            'geographic_bounds': {
                'lat_min': self.data['latitude'].min() if 'latitude' in self.data.columns else None,
                'lat_max': self.data['latitude'].max() if 'latitude' in self.data.columns else None,
                'lon_min': self.data['longitude'].min() if 'longitude' in self.data.columns else None,
                'lon_max': self.data['longitude'].max() if 'longitude' in self.data.columns else None,
            }
        }
