"""
Logging utilities for the NCAA Wrestling Tournament Tracker
"""
import os
from typing import List
from ncaa_wrestling_tracker import config

# Initialize debug log
debug_log: List[str] = []
problem_cases: List[str] = []

def log_debug(message: str) -> None:
    """Add a message to the debug log"""
    if config.DEBUG_MODE:
        debug_log.append(message)
        print(f"DEBUG: {message}")

def log_problem(message: str) -> None:
    """Add a message to the problem cases log"""
    problem_cases.append(message)
    print(f"PROBLEM: {message}")

def save_debug_log() -> None:
    """Save the debug log to a file"""
    if config.DEBUG_MODE and debug_log:
        with open(config.OUTPUT_DEBUG, 'w') as f:
            f.write('\n'.join(debug_log))
        print(f"Debug log saved to {config.OUTPUT_DEBUG}")

def save_problem_cases() -> None:
    """Save problem cases to a file"""
    if problem_cases:
        with open(config.OUTPUT_PROBLEM_CASES, 'w') as f:
            f.write('\n'.join(problem_cases))
        print(f"Problem cases saved to {config.OUTPUT_PROBLEM_CASES}")