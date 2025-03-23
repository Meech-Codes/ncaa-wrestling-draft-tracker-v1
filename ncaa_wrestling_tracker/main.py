"""
Main application module for the NCAA Wrestling Tournament Draft Tracker
"""
import os
import sys
import pandas as pd

from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug, log_problem, save_debug_log, save_problem_cases
from ncaa_wrestling_tracker.utils.file_utils import create_output_directory, save_input_copy, save_draft_copy, create_readme
from ncaa_wrestling_tracker.data.data_loader import load_draft_data, load_results_text, validate_input_files
from ncaa_wrestling_tracker.data.data_saver import save_results_to_csv, save_text_report, save_mismatches
from ncaa_wrestling_tracker.processors.wrestler_matcher import build_wrestler_lookup
from ncaa_wrestling_tracker.processors.results_processor import parse_wrestling_results
from ncaa_wrestling_tracker.processors.scorer import calculate_team_points
from ncaa_wrestling_tracker.reports.report_generator import generate_detailed_report, generate_summary_report
from ncaa_wrestling_tracker.reports.analytics import debug_wrestler

def main(return_results=False):
    """Main application function"""
    print(f"\nNCAA Wrestling Tournament Draft Tracker")
    print(f"======================================")
    
    # Create output directory
    create_output_directory()
    print(f"Output directory: {config.OUTPUT_DIR}")
    
    # Validate input files
    if not validate_input_files():
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame()) if return_results else None
    
    # Save copies of the input files
    save_input_copy(config.OUTPUT_DIR, config.RESULTS_FILE)
    save_draft_copy(config.OUTPUT_DIR, config.DRAFT_CSV)
    
    # Load drafted wrestlers from CSV
    try:
        drafted_wrestlers = load_draft_data(config.DRAFT_CSV)
        print(f"Successfully loaded {sum(len(team) for team in drafted_wrestlers.values())} wrestlers from {len(drafted_wrestlers)} teams")
    except Exception as e:
        print(f"Error loading draft data: {e}")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame()) if return_results else None
    
    # Load results text from file
    try:
        results_text = load_results_text(config.RESULTS_FILE)
        print(f"Successfully loaded results from {config.RESULTS_FILE}")
    except Exception as e:
        print(f"Error loading results file: {e}")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame()) if return_results else None
    
    # Build the wrestler lookup tables
    wrestler_lookup, weight_seed_lookup, all_wrestlers, problem_wrestler_info = build_wrestler_lookup(drafted_wrestlers)
    
    # Parse results and calculate points
    try:
        results_df, round_df, placements_df = parse_wrestling_results(
            results_text, drafted_wrestlers, wrestler_lookup, weight_seed_lookup, all_wrestlers, problem_wrestler_info
        )
        print(f"Successfully processed results for {len(results_df)} wrestlers")
    except Exception as e:
        print(f"Error processing results: {e}")
        import traceback
        traceback.print_exc()
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame()) if return_results else None
    
    # Calculate team points
    team_summary = calculate_team_points(results_df)
    
    # Generate detailed report
    try:
        report = generate_detailed_report(results_df, team_summary, config.RESULTS_FILE)
        save_text_report(report)
    except Exception as e:
        print(f"Error generating report: {e}")
        return (results_df, round_df, placements_df) if return_results else None
    
    # Save results to files
    try:
        save_results_to_csv(results_df, team_summary, round_df, placements_df)
    except Exception as e:
        print(f"Error saving results: {e}")
        return (results_df, round_df, placements_df) if return_results else None
    
    # Save the debug log and problem cases
    save_debug_log()
    save_problem_cases()
    
    # Create README file
    create_readme(config.OUTPUT_DIR)
    
    # Display summary
    summary = generate_summary_report(team_summary)
    print("\n" + summary)
    
    # Return results if requested
    if return_results:
        return results_df, round_df, placements_df