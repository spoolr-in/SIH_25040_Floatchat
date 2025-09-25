#!/usr/bin/env python3
"""
Data Consolidation Script for FloatChat
This script consolidates ARGO float data from multiple directories into a single master dataset.

Phase 1 of the FloatChat project as per the plan:
- Merges measurements and trajectory data
- Adds float_id column for tracking
- Saves to master_dataset.parquet
"""

import pandas as pd
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_float_data(float_dir_path):
    """
    Load and merge measurements and trajectory data for a single float.
    
    Args:
        float_dir_path (str): Path to float directory containing parquet files
        
    Returns:
        pd.DataFrame: Merged dataframe with measurements and trajectory data
    """
    try:
        # Load measurements data
        measurements_path = os.path.join(float_dir_path, 'measurements.parquet')
        trajectory_path = os.path.join(float_dir_path, 'trajectory.parquet')
        
        if not os.path.exists(measurements_path) or not os.path.exists(trajectory_path):
            logger.warning(f"Missing files in {float_dir_path}")
            return None
            
        measurements = pd.read_parquet(measurements_path)
        trajectory = pd.read_parquet(trajectory_path)
        
        # Add trajectory sequence number for merging
        trajectory = trajectory.reset_index()
        trajectory['profile_id'] = trajectory.index + 1
        
        # Merge measurements with trajectory data
        merged_data = pd.merge(measurements, trajectory, on='profile_id', how='left')
        
        # Extract float_id from directory name
        float_id = os.path.basename(float_dir_path)
        merged_data['float_id'] = float_id
        
        logger.info(f"Processed float {float_id}: {len(merged_data)} records")
        return merged_data
        
    except Exception as e:
        logger.error(f"Error processing {float_dir_path}: {str(e)}")
        return None

def consolidate_data(data_root_dir, output_path):
    """
    Consolidate all float data into a single master dataset.
    
    Args:
        data_root_dir (str): Root directory containing float data
        output_path (str): Path to save the consolidated dataset
    """
    logger.info("Starting data consolidation process...")
    
    all_data = []
    processed_floats = 0
    
    # Navigate to the nested data directory
    data_dir = os.path.join(data_root_dir, 'drive-download-20250924T143019Z-1-001')
    
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    # Process each float directory
    for item in os.listdir(data_dir):
        float_path = os.path.join(data_dir, item)
        
        if os.path.isdir(float_path):
            logger.info(f"Processing float: {item}")
            float_data = load_float_data(float_path)
            
            if float_data is not None:
                all_data.append(float_data)
                processed_floats += 1
            else:
                logger.warning(f"Skipped float: {item}")
    
    if not all_data:
        logger.error("No data found to consolidate")
        return
    
    # Combine all data
    logger.info(f"Combining data from {processed_floats} floats...")
    master_dataset = pd.concat(all_data, ignore_index=True)
    
    # Clean and optimize the dataset
    logger.info("Cleaning and optimizing dataset...")
    
    # Remove rows with missing critical data
    master_dataset = master_dataset.dropna(subset=['latitude', 'longitude', 'date'])
    
    # Sort by date for better performance
    master_dataset = master_dataset.sort_values('date')
    
    # Optimize data types
    master_dataset['float_id'] = master_dataset['float_id'].astype('category')
    master_dataset['pressure'] = pd.to_numeric(master_dataset['pressure'], errors='coerce')
    master_dataset['temperature'] = pd.to_numeric(master_dataset['temperature'], errors='coerce')
    master_dataset['salinity'] = pd.to_numeric(master_dataset['salinity'], errors='coerce')
    
    # Save the consolidated dataset
    logger.info(f"Saving master dataset to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    master_dataset.to_parquet(output_path, compression='snappy')
    
    # Print summary statistics
    logger.info("=== Consolidation Complete ===")
    logger.info(f"Total records: {len(master_dataset):,}")
    logger.info(f"Float count: {master_dataset['float_id'].nunique()}")
    logger.info(f"Date range: {master_dataset['date'].min()} to {master_dataset['date'].max()}")
    logger.info(f"Columns: {list(master_dataset.columns)}")
    logger.info(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    
    # Print parameter statistics
    print("\n=== Parameter Statistics ===")
    for param in ['temperature', 'salinity', 'pressure']:
        if param in master_dataset.columns:
            non_null = master_dataset[param].notna().sum()
            print(f"{param.capitalize()}: {non_null:,} measurements")
    
    return master_dataset

def main():
    """Main execution function"""
    # Define paths
    project_root = Path(__file__).parent.parent
    data_root = project_root / 'data'
    output_path = project_root / 'processed_data' / 'master_dataset.parquet'
    
    logger.info(f"Project root: {project_root}")
    logger.info(f"Data root: {data_root}")
    logger.info(f"Output path: {output_path}")
    
    # Run consolidation
    consolidate_data(str(data_root), str(output_path))

if __name__ == "__main__":
    main()
