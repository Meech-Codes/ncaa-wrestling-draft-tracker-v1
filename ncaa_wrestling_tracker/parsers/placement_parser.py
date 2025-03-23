"""
Placement parsing functionality for the NCAA Wrestling Tournament Tracker
"""
import re
from typing import Optional, Dict, Any
from ncaa_wrestling_tracker.utils.logging_utils import log_debug


def parse_placement_line(line: str, current_weight: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Parse lines that explicitly state a wrestler's placement
    
    Example format: "1st: John Smith (Iowa State)"
    
    Args:
        line: Line of text to parse
        current_weight: Current weight class being processed
        
    Returns:
        Dictionary with placement information or None if parsing fails
    """
    placement_pattern = r"(\d+)(?:st|nd|rd|th):\s+(.*?)\s+\((.*?)\)"
    match = re.search(placement_pattern, line)
    
    if match:
        placement = int(match.group(1))
        wrestler_name = match.group(2).strip()
        wrestler_school = match.group(3).strip()
        
        log_debug(f"Found placement: {placement} - {wrestler_name} ({wrestler_school})")
        
        return {
            'placement': placement,
            'wrestler_name': wrestler_name,
            'wrestler_school': wrestler_school,
            'weight': current_weight
        }
    
    return None