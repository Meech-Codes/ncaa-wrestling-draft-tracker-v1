"""
Configuration settings for the NCAA Wrestling Tournament Draft Tracker
"""
import os
import datetime

# Set base file paths - updated for new structure
PROJECT_ROOT = r"C:\Users\Admin\Documents\Python Projects\ncaa-wrestling-draft-tracker-beta"
DATA_PATH = os.path.join(PROJECT_ROOT, "Data")
RESULTS_FILE = os.path.join(DATA_PATH, "wrestling_results.txt")
DRAFT_CSV = os.path.join(DATA_PATH, "ncaa_wrestling_draft.csv")

# Enable debugging output
DEBUG_MODE = True

# Create Results folder with timestamped subfolders
RESULTS_BASE = os.path.join(PROJECT_ROOT, "Results")
if not os.path.exists(RESULTS_BASE):
    os.makedirs(RESULTS_BASE)
    
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR = os.path.join(RESULTS_BASE, timestamp)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
# Output file paths
OUTPUT_WRESTLER_CSV = os.path.join(OUTPUT_DIR, "wrestler_results.csv")
OUTPUT_TEAM_CSV = os.path.join(OUTPUT_DIR, "team_standings.csv")
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "tournament_report.txt")
OUTPUT_DEBUG = os.path.join(OUTPUT_DIR, "debug_log.txt")
OUTPUT_MISMATCHES = os.path.join(OUTPUT_DIR, "mismatched_wrestlers.csv")
OUTPUT_ROUND_SUMMARY = os.path.join(OUTPUT_DIR, "round_by_round_summary.csv")
OUTPUT_PROBLEM_CASES = os.path.join(OUTPUT_DIR, "problem_cases.txt")
OUTPUT_PLACEMENTS = os.path.join(OUTPUT_DIR, "wrestler_placements.csv")

# Define problematic wrestlers to watch
PROBLEM_WRESTLERS = [
    'Smith', 'Knox', 'Koderhandt', 'Composto', 'Johnson', 'Thomson', 
    'Thompson', 'Thomsen', 'Voelker', 'Kueter', 'Keuter', 'Scott', 'Edmond', 'O\'Toole'
]

# Define placement point values according to NCAA rules
PLACEMENT_POINTS = {
    1: 16,   # 1st place
    2: 12,   # 2nd place
    3: 10,   # 3rd place
    4: 9,    # 4th place
    5: 7,    # 5th place
    6: 6,    # 6th place
    7: 4,    # 7th place
    8: 3     # 8th place
}

# School name standardization mapping
SCHOOL_MAPPINGS = {
    'virginia tech': 'virginia tech',
    'viginia tech': 'virginia tech',
    'vt': 'virginia tech',
    'virginia': 'virginia',
    'uva': 'virginia',
    'penn state': 'penn state',
    'psu': 'penn state',
    'ohio state': 'ohio state',
    'osu': 'ohio state',
    'unc': 'north carolina',
    'north carolina': 'north carolina',
    'iowa state': 'iowa state',
    'isu': 'iowa state',
    'south dakota state': 'south dakota state',
    'south dakota': 'south dakota',
    'cal poly': 'cal poly',
    'ncsu': 'nc state',
    'nc state': 'nc state',
    'oklahome state': 'oklahoma state',
    'pittburgh': 'pittsburgh',
    'califoria bakersfield': 'csu bakersfield',
    'bakersfield': 'csu bakersfield',
    'csub': 'csu bakersfield',
    'northern': 'northern',  # Handle 'Northern Iowa', 'Northern Colorado', etc.
    'pennsylvania': 'pennsylvania',
    'penn': 'pennsylvania'
}

# Direct name overrides for known problematic wrestlers
DIRECT_NAME_OVERRIDES = {
    "garrett thompson": ("Garrett Thomson", "Ohio", "Lucas G"),
    "caleb smith": ("Caleb Smith", "Nebraska", "Big Cat"),
    "ben kueter": ("Ben Keuter", "Iowa", "Ty Walters")
}

# Weight classes
WEIGHT_CLASSES = ['125', '133', '141', '149', '157', '165', '174', '184', '197', '285']