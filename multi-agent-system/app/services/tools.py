from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from app.core.config import get_settings
import asyncio
from typing import Dict, Any, List
import re

settings = get_settings()

@tool
async def web_search(query: str) -> str:
    """
    Perform web search using Tavily API
    
    Args:
        query: Search query
        
    Returns:
        Formatted search results
    """
    try:
        search = TavilySearchResults(
            max_results=settings.max_search_results,
            api_key=settings.tavily_api_key
        )
        results = await asyncio.to_thread(search.invoke, query)
        
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            formatted.append(f"**{r.get('title', 'No title')}**\n{r.get('content', '')[:200]}...")
        
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def calculate_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate various metrics from data
    
    Args:
        data: Dictionary containing numerical data
        
    Returns:
        Dictionary of calculated metrics
    """
    try:
        numbers = []
        
        # Extract all numbers from data
        for key, value in data.items():
            if isinstance(value, (int, float)):
                numbers.append(value)
            elif isinstance(value, str):
                # Extract numbers from string
                found_numbers = re.findall(r'-?\d+\.?\d*', value)
                numbers.extend([float(n) for n in found_numbers])
        
        if not numbers:
            return {"error": "No numerical data found"}
        
        metrics = {
            "count": len(numbers),
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers)
        }
        
        return metrics
    except Exception as e:
        return {"error": f"Calculation error: {str(e)}"}

@tool
def format_data(data: Any, format_type: str = "json") -> str:
    """
    Format data in specified format
    
    Args:
        data: Data to format
        format_type: Output format (json, csv, markdown)
        
    Returns:
        Formatted data string
    """
    import json
    import csv
    from io import StringIO
    
    try:
        if format_type == "json":
            return json.dumps(data, indent=2)
        
        elif format_type == "csv" and isinstance(data, list):
            output = StringIO()
            if data and isinstance(data[0], dict):
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return output.getvalue()
        
        elif format_type == "markdown":
            if isinstance(data, dict):
                lines = []
                for key, value in data.items():
                    lines.append(f"- **{key}**: {value}")
                return "\n".join(lines)
            elif isinstance(data, list):
                return "\n".join([f"- {item}" for item in data])
        
        return str(data)
    
    except Exception as e:
        return f"Formatting error: {str(e)}"