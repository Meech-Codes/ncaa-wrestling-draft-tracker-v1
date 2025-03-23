"""
Generate detailed reports for the NCAA Wrestling Tournament Tracker
"""
import datetime
from typing import Dict, Any, List
import pandas as pd

def generate_detailed_report(results_df: pd.DataFrame, team_summary_df: pd.DataFrame, 
                           results_file_path: str) -> str:
    """
    Generate a detailed report including team standings and individual wrestler performances
    with correct NCAA scoring breakdown.
    
    Args:
        results_df: DataFrame with wrestler results
        team_summary_df: DataFrame with team standings
        results_file_path: Path to the input results file
        
    Returns:
        String containing the full report
    """
    # Get timestamp for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"NCAA WRESTLING TOURNAMENT DRAFT RESULTS\n"
    report += f"Generated: {timestamp}\n"
    report += f"Source File: {results_file_path}\n"
    report += "=" * 50 + "\n\n"
    
    # Team Standings
    report += "TEAM STANDINGS\n"
    report += "-" * 50 + "\n"
    for i, row in team_summary_df.iterrows():
        report += f"{i+1}. {row['owner']} - {row['total_points']} points\n"
        report += f"   Advancement: {row['total_advancement']} points (Champ: {row['champ_advancement']}, Cons: {row['cons_advancement']})\n"
        report += f"   Bonus: {row['total_bonus']} points (Champ: {row['champ_bonus']}, Cons: {row['cons_bonus']})\n"
        
        # Add placement points if available
        if 'placement_points' in row:
            report += f"   Placement: {row['placement_points']} points\n"
            
        report += f"   Wrestlers with points: {row['Wrestlers with Points']}\n\n"
    
    # Individual Performances by Team
    for team in team_summary_df['owner']:
        report += f"\n{team} WRESTLERS\n"
        report += "-" * 50 + "\n"
        
        team_wrestlers = results_df[results_df['owner'] == team].sort_values('total_points', ascending=False)
        
        for i, wrestler in team_wrestlers.iterrows():
            # Calculate advancement points for this wrestler
            champ_advancement = wrestler.get('champ_advancement', wrestler.get('champ_wins', 0) * 1.0)
            cons_advancement = wrestler.get('cons_advancement', wrestler.get('cons_wins', 0) * 0.5)
            
            report += f"{wrestler['weight']} - {wrestler['Wrestler']} ({wrestler['seed']}): {wrestler['total_points']} points\n"
            report += f"   Advancement: {champ_advancement + cons_advancement} (Champ: {champ_advancement}, Cons: {cons_advancement})\n"
            report += f"   Bonus: {wrestler.get('champ_bonus', 0) + wrestler.get('cons_bonus', 0)} (Champ: {wrestler.get('champ_bonus', 0)}, Cons: {wrestler.get('cons_bonus', 0)})\n"
            
            # Add placement info if available
            if pd.notnull(wrestler.get('placement')) and wrestler.get('placement') is not None:
                report += f"   Placement: {int(wrestler['placement'])}th place ({wrestler.get('placement_points', 0)} points)\n"
            
            # Add match details
            if isinstance(wrestler['matches'], list) and wrestler['matches']:
                for match in wrestler['matches']:
                    match_method_text = ""
                    if 'match_method' in match and match['match_method'] not in ["full_name", "name_only"]:
                        match_method_text = f" [matched by {match['match_method']}]"
                    
                    # Show the full win type description for sudden victory and tie breaker
                    result_text = match['result']
                    if result_text in ['SV', 'TB'] and 'win_type_full' in match:
                        result_text = match['win_type_full']
                    
                    report += f"   {match['round']} - {result_text} over {match['opponent']} ({match['total_points']} pts = {match['advancement_points']} adv + {match['bonus_points']} bonus){match_method_text}\n"
            
            report += "\n"
    
    return report


def generate_summary_report(team_summary_df: pd.DataFrame) -> str:
    """
    Generate a simple summary report of team standings
    
    Args:
        team_summary_df: DataFrame with team standings
        
    Returns:
        String containing the summary report
    """
    report = "TEAM STANDINGS:\n"
    report += "-" * 80 + "\n"
    report += f"{'Rank':<5}{'Team':<25}{'Total':<10}{'Adv':<10}{'Bonus':<10}"
    
    if 'placement_points' in team_summary_df.columns:
        report += f"{'Placement':<10}"
        
    report += "\n" + "-" * 80 + "\n"
    
    for i, row in team_summary_df.iterrows():
        line = f"{i+1:<5}{row['owner']:<25}{row['total_points']:<10}{row['total_advancement']:<10}{row['total_bonus']:<10}"
        
        if 'placement_points' in row:
            line += f"{row['placement_points']:<10}"
            
        report += line + "\n"
        
    return report