"""
Match parsing functionality for the NCAA Wrestling Tournament Tracker
"""
import re
from typing import Optional, Dict, Any, Tuple
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug, log_problem


# Define a mapping of round names to standardized information
ROUND_MAPPING = {
    # Preliminary rounds
    "Prelim": {"bracket": "Champ", "round_num": 0, "full_round": "Prelim", "advancement_points": 1.0},
    "Pig Tails": {"bracket": "Champ", "round_num": 0, "full_round": "Pig Tails", "advancement_points": 1.0},
    
    # Championship bracket rounds
    "Champ. Round 1": {"bracket": "Champ", "round_num": 1, "full_round": "Champ. R1", "advancement_points": 1.0},
    "Champ Round 1": {"bracket": "Champ", "round_num": 1, "full_round": "Champ. R1", "advancement_points": 1.0},
    "Champ. Round 2": {"bracket": "Champ", "round_num": 2, "full_round": "Champ. R2", "advancement_points": 1.0},
    "Champ Round 2": {"bracket": "Champ", "round_num": 2, "full_round": "Champ. R2", "advancement_points": 1.0},
    "Quarterfinal": {"bracket": "Champ", "round_num": 3, "full_round": "Quarters", "advancement_points": 1.0},
    "Semifinal": {"bracket": "Champ", "round_num": 4, "full_round": "Semis", "advancement_points": 1.0},
    "1st Place Match": {"bracket": "Champ", "round_num": 5, "full_round": "Finals", "advancement_points": 0.0},  # No advancement points for finals
    "Championships": {"bracket": "Champ", "round_num": 5, "full_round": "Finals", "advancement_points": 0.0},
    
    # Consolation bracket rounds
    "Consolation Pig Tails": {"bracket": "Cons", "round_num": 0, "full_round": "Cons. Pig Tails", "advancement_points": 0.5},
    "Cons. Pig Tails": {"bracket": "Cons", "round_num": 0, "full_round": "Cons. Pig Tails", "advancement_points": 0.5},
    "Cons. Round 1": {"bracket": "Cons", "round_num": 1, "full_round": "Cons. R1", "advancement_points": 0.5},
    "Cons. Round 2": {"bracket": "Cons", "round_num": 2, "full_round": "Cons. R2", "advancement_points": 0.5},
    "Cons. Round 3": {"bracket": "Cons", "round_num": 3, "full_round": "Cons. R3", "advancement_points": 0.5},
    "Cons. Round 4": {"bracket": "Cons", "round_num": 4, "full_round": "Cons. R4", "advancement_points": 0.5},
    "Cons. Round 5": {"bracket": "Cons", "round_num": 5, "full_round": "Cons. R5", "advancement_points": 0.5},
    "Cons. Semi": {"bracket": "Cons", "round_num": 6, "full_round": "Cons. Semis", "advancement_points": 0.5},
    
    # Placement matches
    "3rd Place Match": {"bracket": "Place", "round_num": 7, "full_round": "3rd Place", "advancement_points": 0.0},
    "5th Place Match": {"bracket": "Place", "round_num": 7, "full_round": "5th Place", "advancement_points": 0.0},
    "7th Place Match": {"bracket": "Place", "round_num": 7, "full_round": "7th Place", "advancement_points": 0.0}
}

# Keep track of section headers to handle prelims correctly
current_section = None


def parse_match_result(match_text: str, current_weight: Optional[str] = None, 
                      section_header: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Parse a single match result text and extract relevant information.
    
    Args:
        match_text: Text describing a match result
        current_weight: Current weight class being processed
        section_header: Current section header (round type) being processed
        
    Returns:
        Dictionary with match information or None if parsing fails
    """
    global current_section
    
    # Update current section if a new one is provided
    if section_header:
        current_section = section_header
    
    # Check if any problematic wrestler is in this line first
    for wrestler in config.PROBLEM_WRESTLERS:
        if wrestler.lower() in match_text.lower():
            log_problem(f"Found problem wrestler match: {match_text}")
    
    # Special handling for prelim matches based on section
    if match_text.startswith("Prelim -"):
        if current_section == "Consolation Pig Tails":
            # This is a consolation prelim
            round_info = ROUND_MAPPING["Consolation Pig Tails"]
        else:
            # This is a championship prelim
            round_info = ROUND_MAPPING["Prelim"]
        
        log_debug(f"Prelim match in section '{current_section}', assigned to {round_info['bracket']} bracket")
    else:
        # Try to determine the round type
        round_info = None
        for round_name, info in ROUND_MAPPING.items():
            if round_name in match_text or match_text.startswith(round_name):
                round_info = info
                break
        
        # Use section header as fallback
        if not round_info and current_section and current_section in ROUND_MAPPING:
            round_info = ROUND_MAPPING[current_section]
            log_debug(f"Using section header '{current_section}' to determine round info")
    
    # Check if this is a placement match
    is_placement_match = False
    if "Place Match" in match_text:
        is_placement_match = True
        log_debug(f"Found placement match: {match_text}")
    
    # Try to parse the match with a flexible pattern
    match_data = _parse_match_with_pattern(match_text, current_weight, round_info, is_placement_match)
    
    if match_data:
        return match_data
    else:
        log_debug(f"Failed to parse line: {match_text}")
        return None


def _parse_match_with_pattern(match_text: str, current_weight: Optional[str], 
                             round_info: Optional[Dict], is_placement_match: bool) -> Optional[Dict[str, Any]]:
    """
    Parse a match with a flexible pattern that works for various round formats
    
    Args:
        match_text: Match text to parse
        current_weight: Current weight class
        round_info: Information about the round
        is_placement_match: Whether this is a placement match
        
    Returns:
        Match information dictionary or None if parsing fails
    """
    # Generic pattern that works for all round formats
    pattern = r"(?:.*?)(?:\s*-\s*)(.*?)\s+\((.*?)\)(?:.*?)won\s+(?:by|in)\s+(.*?)\s+over\s+(.*?)\s+\((.*?)\)(.*)"
    
    match = re.search(pattern, match_text)
    if not match:
        return None
    
    winner_name = match.group(1).strip()
    winner_school = match.group(2).strip()
    win_type_full = match.group(3).strip()
    loser_name = match.group(4).strip()
    loser_school = match.group(5).strip()
    
    # Extract seed info from the match text if available
    winner_seed = None
    winner_seed_num = None
    
    # Look for seed pattern in the match text (after the wrestler's name)
    seed_pattern = r"\(.*?\)\s+(\d+)-\d+\s+(?:\(#(\d+)\))?"
    seed_match = re.search(seed_pattern, match_text)
    if seed_match and seed_match.group(2):
        winner_seed = f"#{seed_match.group(2)}"
        winner_seed_num = int(seed_match.group(2))
    
    # Parse win type and bonus points
    win_type, bonus_points = _parse_win_type(win_type_full, match_text)
    
    # Handle placement matches specifically
    if is_placement_match:
        # Extract the placement number (e.g., "3rd Place Match" -> 3)
        placement_num = None
        for place in ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]:
            if place in match_text:
                placement_num = int(place[0])
                break
        
        # Determine winner and loser placements
        winner_placement = None
        loser_placement = None
        
        if placement_num == 1:  # Finals
            winner_placement = 1
            loser_placement = 2
        elif placement_num == 3:  # 3rd place match
            winner_placement = 3
            loser_placement = 4
        elif placement_num == 5:  # 5th place match
            winner_placement = 5
            loser_placement = 6
        elif placement_num == 7:  # 7th place match
            winner_placement = 7
            loser_placement = 8
        
        return {
            'is_placement_match': True,
            'placement_match': f"{placement_num}{'st' if placement_num == 1 else 'rd' if placement_num == 3 else 'th'} Place",
            'winner_name': winner_name,
            'winner_school': winner_school,
            'winner_placement': winner_placement,
            'winner_seed': winner_seed,
            'winner_seed_num': winner_seed_num,
            'loser_name': loser_name,
            'loser_school': loser_school,
            'loser_placement': loser_placement,
            'weight': current_weight,
            'win_type': win_type,
            'win_type_full': win_type_full,
            'advancement_points': 0.0,  # No advancement points for placement matches
            'bonus_points': bonus_points,
            'total_points': bonus_points,  # Only bonus points in placement matches
            'match_text': match_text
        }
    
    # For non-placement matches
    if round_info:
        bracket = round_info["bracket"]
        round_num = round_info["round_num"]
        full_round = round_info["full_round"]
        advancement_points = round_info["advancement_points"]
    else:
        # Default to championship bracket if we couldn't determine the round
        log_debug(f"Could not determine round for: {match_text}, defaulting to championship bracket")
        bracket = "Champ"
        round_num = 0
        full_round = "Unknown"
        advancement_points = 1.0
    
    # Double check for specifically problematic formats
    if "(SV-1" in match_text or " SV-1 " in match_text:
        win_type = "SV"
        win_type_full = "sudden victory"
        log_problem(f"SV-1 pattern detected: {match_text}")
    elif "(TB-1" in match_text or " TB-1 " in match_text:
        win_type = "TB"
        win_type_full = "tie breaker"
        log_problem(f"TB-1 pattern detected: {match_text}")
    
    # Calculate total points (advancement + bonus)
    total_points = advancement_points + bonus_points
    
    if win_type in ["SV", "TB"]:
        log_problem(f"Detected {win_type} match: {match_text}")
    
    # Return the parsed match info
    return {
        'is_placement_match': False,
        'bracket': bracket,
        'round_num': round_num,
        'full_round': full_round,
        'winner_name': winner_name,
        'winner_school': winner_school,
        'winner_seed': winner_seed,
        'winner_seed_num': winner_seed_num,
        'weight': current_weight,
        'loser_name': loser_name,
        'loser_school': loser_school,
        'win_type': win_type,
        'win_type_full': win_type_full,
        'advancement_points': advancement_points,
        'bonus_points': bonus_points,
        'total_points': total_points,
        'match_text': match_text
    }


def _parse_win_type(win_type_full: str, match_text: str) -> Tuple[str, float]:
    """
    Parse the win type and determine bonus points
    
    Args:
        win_type_full: Full description of win type
        match_text: Full match text for additional context
        
    Returns:
        Tuple of (win_type, bonus_points)
    """
    # Handle different win types - robust detection
    if "tech fall" in win_type_full:
        bonus_points = 1.5
        win_type = "TF"
    elif "major decision" in win_type_full:
        bonus_points = 1.0
        win_type = "MD"
    elif any(x in win_type_full for x in ["fall", "pin"]) and "tech fall" not in win_type_full:
        bonus_points = 2.0
        win_type = "Fall"
    elif any(x in win_type_full for x in ["default", "forfeit", "disqualification", "misconduct"]):
        bonus_points = 2.0
        win_type = "Def/DQ"
    elif "sudden victory" in win_type_full or win_type_full.startswith("sudden victory"):
        bonus_points = 0.0
        win_type = "SV"
    elif "tie breaker" in win_type_full or win_type_full.startswith("tie breaker"):
        bonus_points = 0.0
        win_type = "TB"
    elif "decision" in win_type_full:
        bonus_points = 0.0
        win_type = "Dec"
    else:
        # Check the entire match text for patterns
        if "sudden victory" in match_text or " SV-1 " in match_text or " SV-2 " in match_text or "(SV-1" in match_text:
            bonus_points = 0.0
            win_type = "SV"
        elif "tie breaker" in match_text or " TB-1 " in match_text or " TB-2 " in match_text or "(TB-1" in match_text:
            bonus_points = 0.0
            win_type = "TB"
        else:
            bonus_points = 0.0
            win_type = "Other"
    
    return win_type, bonus_points


def analyze_win_types(results_text: str) -> None:
    """
    Extract and analyze all win type formats in the results
    
    Args:
        results_text: Full text of results
    """
    win_types = set()
    for line in results_text.split('\n'):
        if "won by" in line or "won in" in line:
            # Extract the win type portion
            win_start = line.find("won by ") 
            if win_start == -1:
                win_start = line.find("won in ")
            
            if win_start != -1:
                win_start += 7  # Length of "won by " or "won in "
                win_end = line.find(" over", win_start)
                if win_end != -1:
                    win_type = line[win_start:win_end].strip()
                    win_types.add(win_type)
    
    # Log all win types found
    log_problem("ALL WIN TYPES FOUND:")
    for win_type in sorted(win_types):
        log_problem(f"  - '{win_type}'")


def find_specific_wrestlers(results_text: str, specific_names: list) -> None:
    """
    Find and log all occurrences of specific wrestlers in the results
    
    Args:
        results_text: Full text of results
        specific_names: List of wrestler names to search for
    """
    log_problem("\nSPECIFIC WRESTLER SEARCH:")
    for name in specific_names:
        occurrences = []
        for line in results_text.split('\n'):
            if name in line:
                occurrences.append(line)
        
        log_problem(f"Wrestler '{name}' found in {len(occurrences)} lines:")
        for line in occurrences:
            log_problem(f"  {line}")


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