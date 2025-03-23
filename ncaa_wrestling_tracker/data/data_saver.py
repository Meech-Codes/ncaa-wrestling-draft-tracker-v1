"""
Data saving functions for the NCAA Wrestling Tournament Tracker
"""
import pandas as pd
from ncaa_wrestling_tracker import config


def save_results_to_csv(results_df: pd.DataFrame, team_summary_df: pd.DataFrame, 
                        round_df: pd.DataFrame, placements_df: pd.DataFrame) -> None:
    """
    Save all results to CSV files.
    
    Args:
        results_df: DataFrame with wrestler results
        team_summary_df: DataFrame with team standings
        round_df: DataFrame with round-by-round results
        placements_df: DataFrame with wrestler placements
    """
    # Save wrestler results - drop the matches column which contains lists
    results_df_export = results_df.copy()
    if 'matches' in results_df_export.columns:
        results_df_export = results_df_export.drop('matches', axis=1)
    results_df_export.to_csv(config.OUTPUT_WRESTLER_CSV, index=False)
    print(f"Saved wrestler results to {config.OUTPUT_WRESTLER_CSV}")
    
    # Save team standings
    team_summary_df.to_csv(config.OUTPUT_TEAM_CSV, index=False)
    print(f"Saved team standings to {config.OUTPUT_TEAM_CSV}")
    
    # Save round-by-round summary
    round_df.to_csv(config.OUTPUT_ROUND_SUMMARY, index=False)
    print(f"Saved round-by-round summary to {config.OUTPUT_ROUND_SUMMARY}")
    
    # Save placements
    placements_df.to_csv(config.OUTPUT_PLACEMENTS, index=False)
    print(f"Saved wrestler placements to {config.OUTPUT_PLACEMENTS}")


def save_text_report(report_text: str) -> None:
    """
    Save detailed report to a text file
    
    Args:
        report_text: Text report to save
    """
    with open(config.OUTPUT_REPORT, "w") as f:
        f.write(report_text)
    print(f"Saved detailed report to {config.OUTPUT_REPORT}")


def save_mismatches(mismatches: list) -> None:
    """
    Save mismatched wrestlers to CSV for analysis
    
    Args:
        mismatches: List of dictionaries with mismatch information
    """
    if mismatches:
        pd.DataFrame(mismatches).to_csv(config.OUTPUT_MISMATCHES, index=False)
        print(f"Saved {len(mismatches)} mismatched wrestlers to {config.OUTPUT_MISMATCHES}")