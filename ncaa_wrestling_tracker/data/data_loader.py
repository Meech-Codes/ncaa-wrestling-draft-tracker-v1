"""
Data loading functions for the NCAA Wrestling Tournament Tracker
"""
import csv
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.text_utils import extract_seed_number
from ncaa_wrestling_tracker.utils.logging_utils import log_debug


def load_draft_data(csv_file: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load drafted wrestlers from a CSV file.
    
    Expected CSV format:
    Weight,Wrestler,School,Seed,Team Name
    125,Luke Lilledahl,Penn State,#1,Ty Walters
    ...
    
    Args:
        csv_file: Path to the draft CSV file
        
    Returns:
        Dictionary with team owners as keys and lists of wrestler dictionaries as values
    """
    drafted_wrestlers = defaultdict(list)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            drafted_wrestlers[row['Team Name']].append({
                'weight': row['Weight'],
                'name': row['Wrestler'],
                'school': row['School'],
                'seed': row['Seed'],
                'seed_num': extract_seed_number(row['Seed'])
            })
    
    return dict(drafted_wrestlers)


def load_results_text(results_file: str) -> str:
    """
    Load wrestling results from a text file
    
    Args:
        results_file: Path to the results text file
        
    Returns:
        String containing the full tournament results text
    """
    with open(results_file, 'r') as f:
        return f.read()


def validate_input_files() -> bool:
    """
    Check if required input files exist
    
    Returns:
        True if all files exist, False otherwise
    """
    if not os.path.exists(config.DRAFT_CSV):
        print(f"Error: Draft CSV file not found at {config.DRAFT_CSV}")
        print("Please create this file with columns: Weight,Wrestler,School,Seed,Team Name")
        return False
        
    if not os.path.exists(config.RESULTS_FILE):
        print(f"Error: Results file not found at {config.RESULTS_FILE}")
        print("Please create this file with wrestling match results")
        return False
    
    return True