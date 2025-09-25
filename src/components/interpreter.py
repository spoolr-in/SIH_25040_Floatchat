"""
AI Interpreter Module for FloatChat
Handles natural language query interpretation using LLM or fallback keyword extraction.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

@dataclass
class QueryEntity:
    """Structured representation of extracted query entities"""
    parameter: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    date_range: Optional[Tuple[str, str]] = None
    depth_range: Optional[Tuple[float, float]] = None

class LLMInterpreter:
    """LLM-based query interpreter using Ollama"""
    
    def __init__(self, model_name="gemma2:2b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        # Fallback keyword mappings
        self.parameter_keywords = {
            'temperature': ['temperature', 'temp', 'thermal', 'heat'],
            'salinity': ['salinity', 'salt', 'saline'],
            'pressure': ['pressure', 'depth', 'deep']
        }
        
        self.location_keywords = {
            'arabian sea': ['arabian sea', 'arabia'],
            'bay of bengal': ['bay of bengal', 'bengal'],
            'indian ocean': ['indian ocean', 'indian'],
            'madagascar': ['madagascar'],
            'maldives': ['maldives'],
            'sri lanka': ['sri lanka', 'ceylon']
        }
    
    def extract_entities(self, query: str) -> QueryEntity:
        """Extract entities from natural language query"""
        try:
            # Try LLM first if available
            if self.test_connection():
                return self._extract_with_llm(query)
            else:
                logger.info("LLM not available, using fallback keyword extraction")
                return self._extract_with_keywords(query)
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return self._extract_with_keywords(query)
    
    def _extract_with_llm(self, query: str) -> QueryEntity:
        """Extract entities using LLM"""
        prompt = f"""Analyze this oceanographic data query and extract the following information:

Query: "{query}"

Extract ONLY the following (return 'none' if not mentioned):
1. Parameter: temperature, salinity, or pressure
2. Location: arabian sea, bay of bengal, indian ocean, madagascar, maldives, or sri lanka
3. Date: specific date (YYYY-MM-DD format)
4. Date range: start and end dates (YYYY-MM-DD format)
5. Depth range: min and max depth in meters

Format your response exactly like this:
Parameter: [parameter or none]
Location: [location or none]
Date: [date or none]
Date_range: [start_date,end_date or none]
Depth_range: [min_depth,max_depth or none]"""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=3  # Reduced timeout for faster response
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                return self._parse_llm_response(response_text)
            else:
                raise Exception(f"LLM API returned status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"LLM extraction failed: {str(e)}")
            return self._extract_with_keywords(query)
    
    def _parse_llm_response(self, response: str) -> QueryEntity:
        """Parse structured LLM response"""
        try:
            lines = response.split('\n')
            entities = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip().lower()
                    
                    if value != 'none' and value:
                        entities[key] = value
            
            # Parse extracted values
            parameter = entities.get('parameter')
            location = entities.get('location')
            date = entities.get('date')
            
            # Parse date range
            date_range = None
            if 'date_range' in entities and ',' in entities['date_range']:
                try:
                    start, end = entities['date_range'].split(',')
                    date_range = (start.strip(), end.strip())
                except:
                    pass
            
            # Parse depth range
            depth_range = None
            if 'depth_range' in entities and ',' in entities['depth_range']:
                try:
                    min_d, max_d = entities['depth_range'].split(',')
                    depth_range = (float(min_d.strip()), float(max_d.strip()))
                except:
                    pass
            
            return QueryEntity(
                parameter=parameter,
                location=location,
                date=date,
                date_range=date_range,
                depth_range=depth_range
            )
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            return self._extract_with_keywords(response)
    
    def _extract_with_keywords(self, query: str) -> QueryEntity:
        """Fallback keyword-based entity extraction"""
        query_lower = query.lower()
        
        # Extract parameter
        parameter = None
        for param, keywords in self.parameter_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                parameter = param
                break
        
        # Extract location
        location = None
        for loc, keywords in self.location_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                location = loc
                break
        
        # Extract year/date patterns
        date = None
        date_range = None
        
        # Look for year patterns
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, query)
        
        if len(years) >= 2:
            date_range = (f"{years[0]}-01-01", f"{years[1]}-12-31")
        elif len(years) == 1:
            date = f"{years[0]}-01-01"
        
        # Look for depth patterns
        depth_range = None
        depth_pattern = r'(\d+)\s*-\s*(\d+)\s*m'
        depth_match = re.search(depth_pattern, query_lower)
        if depth_match:
            depth_range = (float(depth_match.group(1)), float(depth_match.group(2)))
        
        return QueryEntity(
            parameter=parameter,
            location=location,
            date=date,
            date_range=date_range,
            depth_range=depth_range
        )
    
    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": "Test",
                    "stream": False
                },
                timeout=8  # Increased timeout for more reliable connection test
            )
            
            if response.status_code == 200:
                result = response.json()
                return 'response' in result and result.get('done', False)
            
            return False
            
        except Exception as e:
            logger.debug(f"LLM connection test failed: {str(e)}")
            return False

def create_interpreter() -> LLMInterpreter:
    """Factory function to create interpreter instance"""
    return LLMInterpreter()
