"""
Text processing utilities for the NCAA Wrestling Tournament Tracker
"""
import re
from typing import Optional
from ncaa_wrestling_tracker import config


def standardize_text(text: str) -> str:
    """
    Standardize text for more flexible matching
    
    Args:
        text: Text to standardize
        
    Returns:
        Standardized text
    """
    if not text:
        return ""
    
    # Lowercase, strip whitespace, replace multiple spaces with single space
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    
    # Remove apostrophes, backticks, and other special characters that might cause matching issues
    text = re.sub(r'[\'`''"",.()-]', '', text)  # Remove apostrophes, backticks, quotes, commas, periods, etc.
    
    # Check if this is a school name and apply mapping
    if text in config.SCHOOL_MAPPINGS:
        return config.SCHOOL_MAPPINGS[text]
    
    return text


def standardize_wrestler_name(name: str) -> str:
    """
    Standardize wrestler names to handle common spelling variations
    
    Args:
        name: Wrestler name to standardize
        
    Returns:
        Standardized wrestler name
    """
    name = standardize_text(name)  # Apply base standardization first
    
    # Handle the Thomson/Thompson variation
    if name in ['thomson', 'thompson']:
        return 'thoms'  # Generic stem that will match either spelling
    
    # Handle Keuter/Kueter variation
    if name in ['keuter', 'kueter']:
        return 'kuet'  # Generic stem that will match either spelling
    
    return name


def extract_seed_number(seed_text: Optional[str]) -> Optional[int]:
    """
    Extract the numeric part from a seed designation
    
    Args:
        seed_text: Seed text (e.g. '#1', '2', etc.)
        
    Returns:
        Seed number as integer or None
    """
    if not seed_text:
        return None
    match = re.search(r'#?(\d+)', seed_text)
    if match:
        return int(match.group(1))
    return None


def extract_round_number(round_text: Optional[str]) -> Optional[int]:
    """
    Extract the round number from round text
    
    Args:
        round_text: Text containing round information
        
    Returns:
        Round number as integer or None
    """
    if not round_text:
        return None
    match = re.search(r'Round (\d+)', round_text)
    if match:
        return int(match.group(1))
    return None