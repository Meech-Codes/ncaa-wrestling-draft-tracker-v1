"""
File handling utilities for the NCAA Wrestling Tournament Tracker
"""
import os
import shutil
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug


def create_output_directory() -> str:
    """
    Create output directory if it doesn't exist
    
    Returns:
        Path to the output directory
    """
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)
        print(f"Created output directory: {config.OUTPUT_DIR}")
    
    return config.OUTPUT_DIR


def save_input_copy(output_dir: str, results_file: str) -> None:
    """
    Save a copy of the input file in the output directory for reference
    
    Args:
        output_dir: Output directory path
        results_file: Results file path
    """
    output_file = os.path.join(output_dir, "input_results.txt")
    try:
        with open(results_file, 'r') as src, open(output_file, 'w') as dst:
            dst.write(src.read())
        print(f"Saved copy of input file to {output_file}")
    except Exception as e:
        print(f"Warning: Could not save input file copy: {e}")


def save_draft_copy(output_dir: str, draft_file: str) -> None:
    """
    Save a copy of the draft CSV in the output directory for reference
    
    Args:
        output_dir: Output directory path
        draft_file: Draft CSV file path
    """
    output_file = os.path.join(output_dir, "draft_data.csv")
    try:
        with open(draft_file, 'r') as src, open(output_file, 'w') as dst:
            dst.write(src.read())
        print(f"Saved copy of draft file to {output_file}")
    except Exception as e:
        print(f"Warning: Could not save draft file copy: {e}")


def create_readme(output_dir: str) -> None:
    """
    Create README file with information about this run
    
    Args:
        output_dir: Output directory path
    """
    import datetime
    
    readme_file = os.path.join(output_dir, "README.txt")
    try:
        with open(readme_file, "w") as f:
            f.write(f"NCAA Wrestling Tournament Results\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Input Files:\n")
            f.write(f"- Draft Data: {config.DRAFT_CSV}\n")
            f.write(f"- Results: {config.RESULTS_FILE}\n\n")
            f.write(f"Output Files:\n")
            f.write(f"- tournament_report.txt: Detailed text report with all results\n")
            f.write(f"- wrestler_results.csv: CSV file with individual wrestler performance\n")
            f.write(f"- team_standings.csv: CSV file with team standings\n")
            f.write(f"- round_by_round_summary.csv: CSV file showing W/L for each wrestler by round\n")
            f.write(f"- wrestler_placements.csv: CSV file with wrestler placements\n")
            f.write(f"- draft_data.csv: Copy of the input draft file\n")
            f.write(f"- input_results.txt: Copy of the input results file\n")
            f.write(f"- debug_log.txt: Detailed processing log\n")
            f.write(f"- problem_cases.txt: Special cases requiring attention\n")
            if os.path.exists(config.OUTPUT_MISMATCHES):
                f.write(f"- mismatched_wrestlers.csv: List of wrestlers that couldn't be matched\n")
        print(f"Created README file: {readme_file}")
    except Exception as e:
        print(f"Warning: Could not create README file: {e}")