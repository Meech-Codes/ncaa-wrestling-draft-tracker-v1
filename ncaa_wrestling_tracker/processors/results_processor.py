"""
Process wrestling tournament results
"""
import re
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug, log_problem
from ncaa_wrestling_tracker.parsers.match_parser import parse_match_result, analyze_win_types, find_specific_wrestlers
from ncaa_wrestling_tracker.parsers.match_parser import ROUND_MAPPING  # Import the round mapping dictionary
from ncaa_wrestling_tracker.parsers.placement_parser import parse_placement_line
from ncaa_wrestling_tracker.processors.wrestler_matcher import get_wrestler_data
from ncaa_wrestling_tracker.processors.scorer import assign_placement_points


def parse_wrestling_results(results_text: str, drafted_wrestlers: Dict[str, List[Dict[str, Any]]], 
                           wrestler_lookup: Dict, weight_seed_lookup: Dict, 
                           all_wrestlers: List, problem_wrestler_info: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Parse wrestling tournament results and calculate points for drafted wrestlers.
    
    Args:
        results_text: String containing tournament match results
        drafted_wrestlers: Dictionary mapping participant names to lists of wrestlers they drafted
        wrestler_lookup: Dictionary for looking up wrestlers by (name, school)
        weight_seed_lookup: Dictionary for looking up wrestlers by (weight, seed)
        all_wrestlers: List of all drafted wrestlers
        problem_wrestler_info: Dictionary of problematic wrestlers
        
    Returns:
        Tuple of (results_df, round_df, placements_df) DataFrames
    """
    try:
        # Analyze win types in the results
        analyze_win_types(results_text)
        
        # Look for specific problem wrestlers
        find_specific_wrestlers(results_text, ["Caleb Smith", "Garrett Thompson", "Ben Kueter"])
        
        # Create dictionaries to store wrestler results
        wrestler_results = defaultdict(lambda: {
            'owner': None,
            'weight': None,
            'seed': None,
            'champ_wins': 0,
            'champ_advancement': 0,
            'champ_bonus': 0,
            'cons_wins': 0,
            'cons_advancement': 0,
            'cons_bonus': 0,
            'placement': None,
            'placement_points': 0,
            'total_points': 0,
            'match_count': 0,
            'matches': []
        })
        
        # Create dictionary to track wrestler placements
        wrestler_placements = {}
        
        # Create a dictionary to track round-by-round results
        round_results = {}
        
        # Initialize round results for all wrestlers
        for wrestler in all_wrestlers:
            wrestler_id = f"{wrestler['name']} ({wrestler['school']})"
            round_results[wrestler_id] = {
                'Owner': wrestler['team'],
                'Weight': wrestler['weight'],
                'Wrestler': wrestler['name'],
                'School': wrestler['school'],
                'Seed': wrestler['seed']
                # Rounds will be added as we process results
            }
        
        # Track matches for debugging
        matches_processed = 0
        matches_found = 0
        matches_missed = 0
        
        # Track special win types
        sv_matches = []
        tb_matches = []
        
        # Track mismatches for analysis
        mismatches = []
        
        # Track all rounds encountered
        all_rounds = set()
        
        # Track matches by wrestler name (for troubleshooting specific wrestlers)
        matches_by_wrestler = defaultdict(list)
        
        # First pass - identify all problematic matches and explicit placements
        current_section = None
        current_weight = None
        for line in results_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header (no hyphen and not a weight class)
            if '-' not in line and not re.match(r'^(125|133|141|149|157|165|174|184|197|285|DH)$', line):
                # Store as a potential section header
                potential_section = line
                # Check if it's a known round type
                for round_name in ROUND_MAPPING.keys():
                    if round_name in potential_section:
                        current_section = potential_section
                        log_debug(f"Found section header: {current_section}")
                        break
                continue
                
            # Check if this is a weight class indicator
            if re.match(r'^(125|133|141|149|157|165|174|184|197|285|DH)$', line):
                current_weight = line
                continue
                
            # Check for explicit placement lines (e.g., "1st: John Smith (Iowa State)")
            placement_info = parse_placement_line(line, current_weight)
            if placement_info:
                wrestler_name = placement_info['wrestler_name']
                wrestler_school = placement_info['wrestler_school']
                placement = placement_info['placement']
                weight = placement_info['weight']
                
                # Create a unique key for this wrestler
                wrestler_key = f"{wrestler_name} ({wrestler_school})"
                
                # Store the placement information
                if wrestler_key not in wrestler_placements:
                    wrestler_placements[wrestler_key] = {
                        'name': wrestler_name,
                        'school': wrestler_school,
                        'weight': weight,
                        'placement': placement,
                        'points': config.PLACEMENT_POINTS.get(placement, 0)
                    }
                    log_debug(f"Recorded placement {placement} for {wrestler_key}")
                continue
                
            # Check for problematic wrestlers
            for wrestler in config.PROBLEM_WRESTLERS:
                if wrestler.lower() in line.lower():
                    # Pre-check if this looks like a sudden victory or tie breaker match
                    if "sudden victory" in line or "SV-1" in line or "tie breaker" in line or "TB-1" in line:
                        log_problem(f"Found potential special match format for {wrestler}: {line}")
                        
                    # Store this match text under this wrestler's name
                    matches_by_wrestler[wrestler].append(line)
        
        # Second pass - do the actual parsing
        current_section = None
        current_weight = None
        for line in results_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if '-' not in line and not re.match(r'^(125|133|141|149|157|165|174|184|197|285|DH)$', line):
                # Store as a potential section header
                potential_section = line
                # Check if it's a known round type
                for round_name in ROUND_MAPPING.keys():
                    if round_name in potential_section:
                        current_section = potential_section
                        log_debug(f"Processing section: {current_section}")
                        break
                continue
                
            # Check if this is a weight class indicator
            if re.match(r'^(125|133|141|149|157|165|174|184|197|285|DH)$', line):
                current_weight = line
                continue
            
            # Parse match result - with more robust handling and passing section header
            match_info = parse_match_result(line, current_weight, current_section)
            if not match_info:
                log_debug(f"Failed to parse line: {line}")
                # Add special handling if this looks like a problematic case
                if any(wrestler.lower() in line.lower() for wrestler in config.PROBLEM_WRESTLERS):
                    log_problem(f"Failed to parse problematic match: {line}")
                    # Try harder to extract match information
                    # This is a simplified extraction for sudden victory and tie breaker matches
                    if "sudden victory" in line or "SV-1" in line:
                        # Extract winner and loser using a very permissive pattern
                        simple_pattern = r"Round \d+ - (.*?) \((.*?)\).*?over (.*?) \((.*?)\)"
                        simple_match = re.search(simple_pattern, line)
                        if simple_match:
                            log_problem(f"Extracted basic match info from SV match: {line}")
                            # Process this match with basic info
                            # (add your special handling here)
                continue
                
            matches_processed += 1
            
            # Handle placement matches
            if match_info.get('is_placement_match', False):
                # Process winner placement
                if match_info.get('winner_placement'):
                    winner_key = f"{match_info['winner_name']} ({match_info['winner_school']})"
                    wrestler_placements[winner_key] = {
                        'name': match_info['winner_name'],
                        'school': match_info['winner_school'],
                        'weight': match_info['weight'],
                        'placement': match_info['winner_placement'],
                        'points': config.PLACEMENT_POINTS.get(match_info['winner_placement'], 0)
                    }
                    log_debug(f"Recorded placement {match_info['winner_placement']} for {winner_key} from placement match")
                
                # Process loser placement
                if match_info.get('loser_placement'):
                    loser_key = f"{match_info['loser_name']} ({match_info['loser_school']})"
                    wrestler_placements[loser_key] = {
                        'name': match_info['loser_name'],
                        'school': match_info['loser_school'],
                        'weight': match_info['weight'],
                        'placement': match_info['loser_placement'],
                        'points': config.PLACEMENT_POINTS.get(match_info['loser_placement'], 0)
                    }
                    log_debug(f"Recorded placement {match_info['loser_placement']} for {loser_key} from placement match")
            
            # Add this round to the set of all rounds
            if 'full_round' in match_info:
                all_rounds.add(match_info['full_round'])
            
            # Track sudden victory and tie breaker matches
            if match_info['win_type'] == 'SV':
                sv_matches.append(line)
                log_problem(f"Confirmed sudden victory match: {line}")
            elif match_info['win_type'] == 'TB':
                tb_matches.append(line)
                log_problem(f"Confirmed tie breaker match: {line}")
            
            #######################################################
            # Process the WINNER
            #######################################################
            
            # Use the helper function to get wrestler data
            winner_data, winner_used_key, winner_match_method = get_wrestler_data(
                match_info, 'winner', wrestler_lookup, weight_seed_lookup, 
                problem_wrestler_info
            )
            
            # If we found a match, record the points and update round results
            if winner_data:
                matches_found += 1
                wrestler_id = f"{winner_data['name']} ({winner_data['school']})"
                
                match_log = f"Match found for {match_info['winner_name']} ({match_info['winner_school']}) using {winner_match_method} match"
                if winner_match_method in ["problem_list", "name_override"]:
                    log_problem(match_log)
                else:
                    log_debug(match_log)
                
                # Update wrestler results
                if wrestler_id not in wrestler_results:
                    wrestler_results[wrestler_id] = {
                        'owner': winner_data['team'],
                        'weight': winner_data['weight'],
                        'seed': winner_data['seed'],
                        'champ_wins': 0,
                        'champ_advancement': 0,
                        'champ_bonus': 0,
                        'cons_wins': 0,
                        'cons_advancement': 0,
                        'cons_bonus': 0,
                        'placement': None,
                        'placement_points': 0,
                        'total_points': 0,
                        'match_count': 0,
                        'matches': []
                    }
                
                result = wrestler_results[wrestler_id]
                
                # Record match details
                match_detail = {
                    'round': match_info['full_round'] if 'full_round' in match_info else 'Placement',
                    'opponent': f"{match_info['loser_name']} ({match_info['loser_school']})",
                    'result': match_info['win_type'],
                    'win_type_full': match_info['win_type_full'],
                    'advancement_points': match_info['advancement_points'],
                    'bonus_points': match_info['bonus_points'],
                    'total_points': match_info['total_points'],
                    'match_method': winner_match_method
                }
                result['matches'].append(match_detail)
                result['match_count'] += 1
                
                # Update points based on bracket
                if match_info.get('is_placement_match', False):
                    # Only count bonus points for placement matches
                    result['total_points'] += match_info['bonus_points']
                elif match_info.get('bracket') == "Champ":
                    result['champ_wins'] += 1
                    result['champ_advancement'] = result['champ_wins'] * 1.0  # Championship advancement points
                    result['champ_bonus'] += match_info['bonus_points']
                    result['total_points'] += match_info['total_points']
                else:
                    result['cons_wins'] += 1
                    result['cons_advancement'] = result['cons_wins'] * 0.5  # Consolation advancement points
                    result['cons_bonus'] += match_info['bonus_points']
                    result['total_points'] += match_info['total_points']
                    
                # Update round-by-round results for the winner
                if wrestler_id in round_results:
                    round_key = match_info['full_round'] if 'full_round' in match_info else 'Placement'
                    # Use the specific win type for special matches
                    if match_info['win_type'] in ['SV', 'TB']:
                        round_results[wrestler_id][round_key] = f"W-{match_info['win_type']}"
                        if winner_match_method in ["problem_list", "name_override"]:
                            log_problem(f"Added W-{match_info['win_type']} for {wrestler_id} in {round_key}")
                    else:
                        round_results[wrestler_id][round_key] = f"W-{match_info['win_type']}"
            else:
                matches_missed += 1
                log_debug(f"NO MATCH FOUND for WINNER: {match_info['winner_name']} ({match_info['winner_school']}), " +
                        f"Weight: {match_info.get('weight', 'Unknown')}, Seed: {match_info.get('winner_seed', 'Unknown')}")
                
                # Record this mismatch for analysis
                mismatches.append({
                    'winner_name': match_info['winner_name'],
                    'winner_school': match_info['winner_school'],
                    'weight': match_info.get('weight'),
                    'seed': match_info.get('winner_seed'),
                    'win_type': match_info['win_type'],
                    'win_type_full': match_info['win_type_full'],
                    'points': match_info['total_points'],
                    'match_text': match_info['match_text']
                })
            
            #######################################################
            # Process the LOSER
            #######################################################
            
            # Use the helper function to get wrestler data
            loser_data, loser_used_key, loser_match_method = get_wrestler_data(
                match_info, 'loser', wrestler_lookup, weight_seed_lookup, 
                problem_wrestler_info
            )
            
            # If we found a match for the loser, update round results
            if loser_data:
                loser_id = f"{loser_data['name']} ({loser_data['school']})"
                
                match_log = f"Match found for LOSER: {match_info['loser_name']} ({match_info['loser_school']}) using {loser_match_method} match"
                if loser_match_method in ["problem_list", "name_override"]:
                    log_problem(match_log)
                else:
                    log_debug(match_log)
                
                # Update round-by-round results for the loser
                if loser_id in round_results:
                    round_key = match_info['full_round'] if 'full_round' in match_info else 'Placement'
                    # Indicate if this was a special match type
                    if match_info['win_type'] in ['SV', 'TB']:
                        round_results[loser_id][round_key] = f"L-{match_info['win_type']}"
                        if loser_match_method in ["problem_list", "name_override"]:
                            log_problem(f"Added L-{match_info['win_type']} for {loser_id} in {round_key}")
                    else:
                        round_results[loser_id][round_key] = "L"
            else:
                log_debug(f"No match found for LOSER: {match_info['loser_name']} ({match_info['loser_school']})")
        
        # Log match statistics
        log_debug(f"Matches processed: {matches_processed}")
        log_debug(f"Matches found: {matches_found}")
        log_debug(f"Matches missed: {matches_missed}")
        log_debug(f"Sudden victory matches: {len(sv_matches)}")
        log_debug(f"Tie breaker matches: {len(tb_matches)}")
        
        # Log special match types
        if sv_matches:
            log_problem("SUDDEN VICTORY MATCHES:")
            for match in sv_matches:
                log_problem(f"  {match}")
        
        if tb_matches:
            log_problem("TIE BREAKER MATCHES:")
            for match in tb_matches:
                log_problem(f"  {match}")
        
        # Log matches by problematic wrestler
        for wrestler, matches in matches_by_wrestler.items():
            if matches:
                log_problem(f"\nMatches for {wrestler}:")
                for match in matches:
                    log_problem(f"  {match}")
        
        # Process placement points
        assign_placement_points(wrestler_results, wrestler_placements)
        
        # Check for missing wrestlers in results
        for team, wrestlers in drafted_wrestlers.items():
            for wrestler in wrestlers:
                wrestler_id = f"{wrestler['name']} ({wrestler['school']})"
                if wrestler_id not in wrestler_results:
                    log_debug(f"No matches found for {wrestler_id} on team {team}")
        
        # Convert results to DataFrame
        results_df = pd.DataFrame.from_dict(wrestler_results, orient='index')
        results_df.index.name = 'Wrestler'
        results_df.reset_index(inplace=True)
        
        # Sort by owner, then weight class
        results_df = results_df.sort_values(['owner', 'weight'])
        
        # Convert round results to DataFrame
        round_df = pd.DataFrame.from_dict(round_results, orient='index')
        round_df.index.name = 'Wrestler ID'
        round_df.reset_index(inplace=True)
        
        # Get the actual available columns that are rounds
        available_rounds = []
        for col in round_df.columns:
            if col in all_rounds:
                available_rounds.append(col)
        
        # Define the desired order for the rounds (only including ones that actually exist)
        round_order = []
        round_categories = [
            'Prelim', 'Pig Tails', 
            'Champ. R1', 'Champ. R2', 'Quarters', 'Semis', 'Finals',
            'Cons. Pig Tails', 'Cons. R1', 'Cons. R2', 'Cons. R3', 'Cons. R4', 'Cons. R5', 'Cons. Semis',
            '3rd Place', '5th Place', '7th Place'
        ]
        
        # Add rounds in the desired order, but only if they exist
        for round_name in round_categories:
            if round_name in available_rounds:
                round_order.append(round_name)
        
        # Add any remaining rounds not in our predefined list
        for round_name in available_rounds:
            if round_name not in round_order:
                round_order.append(round_name)
        
        # Sort the round summary by weight class and seed
        round_df['Weight'] = pd.Categorical(round_df['Weight'], 
                                        categories=['125', '133', '141', '149', '157', '165', 
                                                    '174', '184', '197', '285', 'DH'], 
                                        ordered=True)
        round_df['Seed_Num'] = round_df['Seed'].apply(lambda x: 
                                                    int(re.search(r'#?(\d+)', str(x)).group(1)) 
                                                    if pd.notnull(x) and re.search(r'#?(\d+)', str(x))
                                                    else 999)
        round_df = round_df.sort_values(['Weight', 'Seed_Num'])
        round_df = round_df.drop(columns=['Seed_Num'])
        
        # Reorder the columns to have a logical flow
        cols = ['Weight', 'Wrestler', 'School', 'Seed', 'Owner']
        for col in round_order:
            if col in round_df.columns:
                cols.append(col)
        
        if 'Placement' in round_df.columns:
            cols.append('Placement')
        
        # Only select columns that exist in the DataFrame
        existing_cols = [col for col in cols if col in round_df.columns]
        round_df = round_df[existing_cols]
        
        # Convert placements to DataFrame
        placements_df = pd.DataFrame.from_dict(wrestler_placements, orient='index')
        placements_df.index.name = 'Wrestler ID'
        placements_df.reset_index(inplace=True)
        
        # Log results statistics
        log_debug(f"Total wrestlers with points: {len(results_df)}")
        team_stats = results_df.groupby('owner').size()
        for team, count in team_stats.items():
            log_debug(f"Team {team}: {count} wrestlers with points")
        
        return results_df, round_df, placements_df
        
    except Exception as e:
        import traceback
        print(f"Error in parse_wrestling_results: {e}")
        traceback.print_exc()
        
        # Return empty DataFrames instead of None
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()