"""
Analytics functionality for the NCAA Wrestling Tournament Tracker
"""
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any
from ncaa_wrestling_tracker import config


def debug_wrestler(wrestler_name: str, results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Print detailed debug info for a specific wrestler
    
    Args:
        wrestler_name: Name of the wrestler to debug
        results_df: DataFrame with wrestler results
        
    Returns:
        DataFrame subset containing matching wrestlers
    """
    wrestler_rows = results_df[results_df['Wrestler'].str.contains(wrestler_name, case=False)]
    
    if len(wrestler_rows) == 0:
        print(f"No wrestlers found matching '{wrestler_name}'")
        return pd.DataFrame()
        
    for idx, row in wrestler_rows.iterrows():
        print(f"\nDEBUG INFO FOR: {row['Wrestler']}")
        print(f"Owner: {row['owner']}")
        print(f"Weight: {row['weight']}")
        print(f"Championship wins: {row['champ_wins']}")
        print(f"Consolation wins: {row['cons_wins']}")
        print(f"Total points: {row['total_points']}")
        
        if pd.notnull(row.get('placement')) and row.get('placement') is not None:
            print(f"Placement: {int(row['placement'])}th place ({row.get('placement_points', 0)} points)")
            
        print("\nMatches:")
        
        for match in row['matches']:
            print(f"  {match['round']} - {match['result']} over {match['opponent']} ({match['total_points']} pts)")
            print(f"    Match method: {match.get('match_method', 'unknown')}")
            if 'match_text' in match:
                print(f"    Text: {match['match_text']}")
                
    return wrestler_rows


def team_performance_analysis(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze team performance with detailed breakdowns
    
    Args:
        results_df: DataFrame with wrestler results
        
    Returns:
        DataFrame with team performance analysis
    """
    # Count types of wins by team
    win_types = {}
    
    for _, wrestler in results_df.iterrows():
        team = wrestler['owner']
        if team not in win_types:
            win_types[team] = {
                'Fall': 0, 'TF': 0, 'MD': 0, 'Dec': 0, 'SV': 0, 'TB': 0, 'Other': 0
            }
        
        for match in wrestler['matches']:
            result = match['result']
            if result in win_types[team]:
                win_types[team][result] += 1
            else:
                win_types[team]['Other'] += 1
    
    # Convert to DataFrame
    win_types_df = pd.DataFrame.from_dict(win_types, orient='index')
    
    # Add total wins column
    win_types_df['Total Wins'] = win_types_df.sum(axis=1)
    
    # Calculate percentages
    for col in ['Fall', 'TF', 'MD', 'Dec', 'SV', 'TB', 'Other']:
        win_types_df[f'{col} %'] = (win_types_df[col] / win_types_df['Total Wins'] * 100).round(1)
    
    # Calculate bonus win percentage
    win_types_df['Bonus Win %'] = ((win_types_df['Fall'] + win_types_df['TF'] + win_types_df['MD']) / 
                                  win_types_df['Total Wins'] * 100).round(1)
    
    return win_types_df


def placement_analysis(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze placements by team
    
    Args:
        results_df: DataFrame with wrestler results
        
    Returns:
        DataFrame with placement analysis
    """
    # Count placements by team
    if 'placement' not in results_df.columns:
        return pd.DataFrame()
    
    # Get only wrestlers with placements
    placed_wrestlers = results_df[results_df['placement'].notnull()]
    
    # Count placements by team and placement
    placement_counts = pd.crosstab(placed_wrestlers['owner'], placed_wrestlers['placement'])
    
    # Make sure all placements 1-8 are included
    for place in range(1, 9):
        if place not in placement_counts.columns:
            placement_counts[place] = 0
    
    # Sort columns
    placement_counts = placement_counts[sorted(placement_counts.columns)]
    
    # Add total All-Americans (placements) column
    placement_counts['Total AAs'] = placement_counts.sum(axis=1)
    
    # Calculate placement points
    from .. import config
    for place in range(1, 9):
        if place in placement_counts.columns:
            placement_counts[f'{place}th Points'] = placement_counts[place] * config.PLACEMENT_POINTS.get(place, 0)
    
    placement_counts['Total Placement Points'] = sum(
        placement_counts[f'{place}th Points'] for place in range(1, 9) 
        if f'{place}th Points' in placement_counts.columns
    )
    
    return placement_counts