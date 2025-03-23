"""
NCAA Wrestling Tournament scoring implementation
"""
import pandas as pd
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug

def calculate_team_points(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total points per team/owner with correct NCAA scoring breakdown.
    
    Args:
        results_df: DataFrame with wrestler results
        
    Returns:
        DataFrame with team totals
    """
    # First ensure the proper columns exist
    if 'champ_advancement' not in results_df.columns:
        results_df['champ_advancement'] = results_df['champ_wins'] * 1.0
    
    if 'cons_advancement' not in results_df.columns:
        results_df['cons_advancement'] = results_df['cons_wins'] * 0.5
    
    if 'placement_points' not in results_df.columns:
        results_df['placement_points'] = 0.0
        
    team_summary = results_df.groupby('owner').agg({
        'champ_wins': 'sum',  # Count of championship wins
        'champ_advancement': 'sum',  # Championship advancement points
        'champ_bonus': 'sum',  # Championship bonus points
        'cons_wins': 'sum',  # Count of consolation wins
        'cons_advancement': 'sum',  # Consolation advancement points
        'cons_bonus': 'sum',  # Consolation bonus points
        'placement_points': 'sum',  # Placement points
        'total_points': 'sum',  # Total points
        'Wrestler': 'count'  # Count of wrestlers with points
    }).reset_index()
    
    # Add columns for total advancement and total bonus
    team_summary['total_advancement'] = team_summary['champ_advancement'] + team_summary['cons_advancement']
    team_summary['total_bonus'] = team_summary['champ_bonus'] + team_summary['cons_bonus']
    
    team_summary = team_summary.rename(columns={'Wrestler': 'Wrestlers with Points'})
    team_summary = team_summary.sort_values('total_points', ascending=False)
    
    return team_summary


def assign_placement_points(wrestler_results: dict, wrestler_placements: dict) -> None:
    """
    Process and assign placement points to wrestlers
    
    Args:
        wrestler_results: Dictionary of wrestler results
        wrestler_placements: Dictionary of wrestler placements
    """
    log_debug(f"\nAssigning placement points to wrestlers:")
    for wrestler_id, placement_data in wrestler_placements.items():
        if wrestler_id in wrestler_results:
            placement = placement_data['placement']
            points = placement_data['points']
            
            # Update wrestler's results with placement information
            wrestler_results[wrestler_id]['placement'] = placement
            wrestler_results[wrestler_id]['placement_points'] = points
            wrestler_results[wrestler_id]['total_points'] += points
            
            log_debug(f"  {wrestler_id}: {placement}th place, {points} points")
        else:
            # Try to match this wrestler to someone in our results
            matched = False
            for result_id in wrestler_results.keys():
                if (placement_data['name'] in result_id or 
                    placement_data['school'] in result_id):
                    # Found a potential match
                    placement = placement_data['placement']
                    points = placement_data['points']
                    
                    # Update wrestler's results with placement information
                    wrestler_results[result_id]['placement'] = placement
                    wrestler_results[result_id]['placement_points'] = points
                    wrestler_results[result_id]['total_points'] += points
                    
                    log_debug(f"  Matched {wrestler_id} to {result_id}: {placement}th place, {points} points")
                    matched = True
                    break
            
            if not matched:
                log_debug(f"Could not match placement for {wrestler_id} ({placement_data['placement']}th place)")