"""
Wrestler matching functionality for the NCAA Wrestling Tournament Tracker
"""
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.text_utils import standardize_text, standardize_wrestler_name
from ncaa_wrestling_tracker.utils.logging_utils import log_debug, log_problem


def build_wrestler_lookup(drafted_wrestlers: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict, Dict, List, Dict]:
    """
    Build a flexible lookup table for wrestlers
    
    Args:
        drafted_wrestlers: Dictionary of drafted wrestlers by team
        
    Returns:
        Tuple of (wrestler_lookup, weight_seed_lookup, all_wrestlers, problem_wrestler_info)
    """
    wrestler_lookup = {}
    weight_seed_lookup = {}  # For fallback matching by weight and seed
    all_wrestlers = []  # To keep track of all drafted wrestlers for the round summary
    
    # Store problematic wrestler info for reference
    problem_wrestler_info = {}
    
    for team, wrestlers in drafted_wrestlers.items():
        for wrestler in wrestlers:
            # Store the original name and school
            original_name = wrestler['name']
            original_school = wrestler['school']
            weight = wrestler['weight']
            seed = wrestler['seed']
            seed_num = wrestler['seed_num']
            
            # Check if this is a problematic wrestler
            is_problematic = False
            for prob_name in config.PROBLEM_WRESTLERS:
                if prob_name.lower() in original_name.lower():
                    is_problematic = True
                    problem_wrestler_info[original_name] = {
                        'team': team,
                        'weight': weight,
                        'seed': seed,
                        'school': original_school
                    }
                    log_problem(f"Found problematic wrestler in draft: {original_name} ({original_school}) - {weight} {seed}")
            
            # Standard key - name and school exactly as in the spreadsheet
            std_name = standardize_wrestler_name(original_name)
            std_school = standardize_text(original_school)
            
            # Store the data
            data = {
                'team': team,
                'weight': weight,
                'seed': seed,
                'seed_num': seed_num,
                'name': original_name,  # Keep original capitalization
                'school': original_school,  # Keep original capitalization
                'std_name': std_name,  # For reference
                'std_school': std_school  # For reference
            }
            
            # Add to all wrestlers list
            all_wrestlers.append(data)
            
            # Regular key (with standardized text)
            key = (std_name, std_school)
            wrestler_lookup[key] = data
            
            # Also create a name-only key
            name_only_key = (std_name, '')
            if name_only_key not in wrestler_lookup:
                wrestler_lookup[name_only_key] = data
            
            # Also create an alternative key with just the wrestler's last name
            last_name = std_name.split()[-1] if std_name else ""
            alt_key = (last_name, std_school)
            
            # Don't overwrite existing entries with the alt key
            # This prevents confusion between wrestlers with same last name
            if alt_key not in wrestler_lookup:
                wrestler_lookup[alt_key] = data
            
            # Create a weight-seed key for fallback matching
            if weight and seed_num:
                weight_seed_key = (weight, seed_num)
                # Only overwrite if there's a collision if we're confident this is a higher seed
                if weight_seed_key not in weight_seed_lookup or seed_num < weight_seed_lookup[weight_seed_key]['seed_num']:
                    weight_seed_lookup[weight_seed_key] = data
            
            # Log the wrestler and their keys
            log_message = f"Added wrestler: {original_name} ({original_school}) - Team: {team}, Weight: {weight}, Seed: {seed}"
            if is_problematic:
                log_problem(log_message)
                log_problem(f"  - Primary Key: {key}")
                log_problem(f"  - Name-only Key: {name_only_key}")
                log_problem(f"  - Last Name Key: {alt_key}")
                if weight and seed_num:
                    log_problem(f"  - Weight-Seed Key: {weight_seed_key}")
            else:
                log_debug(log_message)
                log_debug(f"  - Primary Key: {key}")
                log_debug(f"  - Name-only Key: {name_only_key}")
                log_debug(f"  - Last Name Key: {alt_key}")
                if weight and seed_num:
                    log_debug(f"  - Weight-Seed Key: {weight_seed_key}")
    
    # Log total wrestlers loaded
    log_debug(f"Total wrestlers in lookup: {len(wrestler_lookup)}")
    log_debug(f"Total weight-seed combinations: {len(weight_seed_lookup)}")
    
    return wrestler_lookup, weight_seed_lookup, all_wrestlers, problem_wrestler_info


def get_wrestler_data(match_info: Dict[str, Any], wrestler_key: str, 
                     wrestler_lookup: Dict, weight_seed_lookup: Dict, 
                     problem_wrestler_info: Dict) -> Tuple[Optional[Dict], Optional[Tuple], Optional[str]]:
    """
    Get wrestler data using flexible matching
    
    Args:
        match_info: Dictionary with match information
        wrestler_key: 'winner' or 'loser' to indicate which wrestler to process
        wrestler_lookup: Dictionary of wrestlers by standardized (name, school)
        weight_seed_lookup: Dictionary of wrestlers by (weight, seed)
        problem_wrestler_info: Dictionary of problematic wrestlers
        
    Returns:
        Tuple of (wrestler_data, used_key, match_method)
    """
    wrestler_name = match_info[f'{wrestler_key}_name']
    wrestler_school = match_info[f'{wrestler_key}_school']
    
    # Standardize information for lookup
    name = standardize_text(wrestler_name)
    school = standardize_text(wrestler_school)
    last_name = name.split()[-1] if name else ""
    
    # Collect weight and seed information if available
    weight = match_info.get('weight')
    seed_num = match_info.get(f'{wrestler_key}_seed_num') if f'{wrestler_key}_seed_num' in match_info else None
    
    # Check for direct override
    std_wrestler_full = f"{name}".lower()
    if std_wrestler_full in config.DIRECT_NAME_OVERRIDES:
        override_name, override_school, override_team = config.DIRECT_NAME_OVERRIDES[std_wrestler_full]
        log_problem(f"DIRECT NAME OVERRIDE for {wrestler_key}: {wrestler_name} -> {override_name}")
        
        # Match this override to a wrestler in our draft data
        for owner_team, wrestlers in wrestler_lookup.items():
            for wrestler_key, wrestler_data in wrestler_lookup.items():
                if wrestler_data['name'] == override_name and wrestler_data['school'] == override_school:
                    used_key = "direct_override"
                    match_method = "name_override"
                    return wrestler_data, used_key, match_method
    
    # Special handling for problematic wrestlers - check if this wrestler is in our problem list
    # IMPROVED MATCHING LOGIC FOR PROBLEMATIC WRESTLERS
    for wrestler_name_prob, info in problem_wrestler_info.items():
        std_wrestler = standardize_text(wrestler_name_prob)
        std_match_wrestler = standardize_text(wrestler_name)
        
        # Get first and last names for both wrestlers
        wrestler_parts = std_wrestler.split()
        match_parts = std_match_wrestler.split()
        
        # More precise matching to avoid mixing up wrestlers with same last name
        is_match = False
        
        # Check if full names match exactly
        if std_wrestler == std_match_wrestler:
            is_match = True
        # Check if weight classes match (if available)
        elif (weight and info['weight'] and weight == info['weight'] and
              # And last names match
              wrestler_parts[-1] == match_parts[-1]):
            is_match = True
        # Check if first AND last names match (more strict than just last name)
        elif (len(wrestler_parts) > 1 and len(match_parts) > 1 and
              wrestler_parts[0] == match_parts[0] and  # First name matches
              wrestler_parts[-1] == match_parts[-1]):  # Last name matches
            is_match = True
        
        if is_match:
            # It's a problematic wrestler - use the known data directly
            log_problem(f"DIRECT MATCH for problematic {wrestler_key}: {wrestler_name} -> {wrestler_name_prob}")
            wrestler_data = {
                'team': info['team'],
                'weight': info['weight'],
                'seed': info['seed'],
                'name': wrestler_name_prob,
                'school': info['school']
            }
            used_key = "direct_problem_match"
            match_method = "problem_list"
            return wrestler_data, used_key, match_method
    
    # Method 1: Try exact name and school
    key = (name, school)
    if key in wrestler_lookup:
        return wrestler_lookup[key], key, "full_name"
    
    # Method 1b: Try name-only match
    name_only_key = (name, '')
    if name_only_key in wrestler_lookup:
        return wrestler_lookup[name_only_key], name_only_key, "name_only"
    
    # Method 2: Try last name and school
    alt_key = (last_name, school)
    if alt_key in wrestler_lookup:
        return wrestler_lookup[alt_key], alt_key, "last_name"
    
    # Method 3: Try weight class and seed as a last resort (only for the winner typically)
    if weight and seed_num and wrestler_key == 'winner':
        weight_seed_key = (weight, seed_num)
        if weight_seed_key in weight_seed_lookup:
            wrestler_data = weight_seed_lookup[weight_seed_key]
            
            # Log this special case
            log_debug(f"WEIGHT-SEED MATCH: {wrestler_name} ({wrestler_school}) " +
                    f"matched to {wrestler_data['name']} ({wrestler_data['school']}) " +
                    f"using weight={weight}, seed={seed_num}")
            
            return wrestler_data, weight_seed_key, "weight_seed"
    
    # No match found
    return None, None, None