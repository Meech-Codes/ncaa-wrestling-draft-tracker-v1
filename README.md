**NCAA Wrestling Tournament Draft Tracker**
======================================

A tool for tracking wrestler performance in NCAA tournaments for fantasy drafts.

**Overview**
------------

This project provides a comprehensive solution for tracking NCAA wrestling tournament results, including wrestler performance, team standings, and detailed reports. The tool is designed to help fantasy draft participants make informed decisions by analyzing wrestler performance across different weight classes and tournaments.

**Features**
------------

* Tracks wrestler performance in NCAA tournaments
* Provides team standings and detailed reports
* Analyzes wrestler performance across different weight classes and tournaments
* Offers a user-friendly interface for easy navigation and data visualization

**Requirements**
---------------

* Python 3.6+
* Streamlit
* Pandas
* Matplotlib
* NumPy
* Pytz
* Seaborn
* Plotly

**Installation**
------------

To install the required dependencies, run the following command:
```bash
pip install -r requirements.txt
```
**Usage**
-----

To run the application, execute the following command:
```bash
streamlit run app.py
```
This will launch the web application, allowing you to interact with the data and visualizations.

**Data**
------

The project uses data from NCAA wrestling tournaments, which is stored in the `Data` directory. The data is loaded into the application using the `load_draft_data` and `load_results_text` functions.

The following data tables are available for analysis:

### Wrestler Data

| Field Name | Description |
| --- | --- |
| `wrestler_id` | Unique identifier for each wrestler |
| `name` | Wrestler's name |
| `weight_class` | Weight class of the wrestler |
| `team` | Wrestler's team |
| `wins` | Number of wins in the tournament |
| `losses` | Number of losses in the tournament |
| `points` | Total points scored by the wrestler |

### Team Data

| Field Name | Description |
| --- | --- |
| `team_id` | Unique identifier for each team |
| `name` | Team name |
| `wins` | Number of wins in the tournament |
| `losses` | Number of losses in the tournament |
| `points` | Total points scored by the team |

### Tournament Data

| Field Name | Description |
| --- | --- |
| `tournament_id` | Unique identifier for each tournament |
| `name` | Tournament name |
| `date` | Date of the tournament |
| `location` | Location of the tournament |

### Match Data

| Field Name | Description |
| --- | --- |
| `match_id` | Unique identifier for each match |
| `wrestler1_id` | ID of the first wrestler in the match |
| `wrestler2_id` | ID of the second wrestler in the match |
| `winner_id` | ID of the winner of the match |
| `score` | Score of the match |

## Features

### Team Standings Dashboard

The Team Standings dashboard provides a comprehensive view of each team's performance in the tournament. Features include:
- Horizontal bar chart showing total points by team
- Detailed breakdown of advancement, bonus, and placement points
- Sortable data table with key metrics

[Add screenshot of Team Standings page here]

### Round-by-Round Results

Track the progress of each wrestler through every round of the tournament with:
- Color-coded win/loss indicators
- Filters by weight class and team
- Special indicators for different victory types (Fall, Tech, Decision, SV, TB)

[Add screenshot of Round-by-Round page here]

### Wrestler Details

Dive deep into individual wrestler performance with:
- Complete match history for each wrestler
- Detailed point breakdowns (advancement, bonus, placement)
- Filters by team and weight class

[Add screenshot of Wrestler Details page here]

### Placements Tracker

Monitor final placements with:
- Comprehensive list of wrestler placements
- Filters by weight class and team owner
- Sortable results by placement and weight class

[Add screenshot of Placements page here]

### Analytics Dashboard

Advanced analytics features include:
- Points breakdown visualization showing the composition of team points
- Weight class heatmap highlighting team strengths across weight classes
- All-Americans distribution by team and placement
- Efficiency metrics comparing points per wrestler and bonus point percentage

[Add screenshot of Analytics dashboard here]

**Configuration**
-------------

The project uses a configuration file (`config.py`) to store settings and file paths. You can modify this file to customize the application's behavior.

**Contributing**
------------

Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request with your changes.

**License**
-------

This project is licensed under the MIT License. See the `LICENSE` file for details.


# Data Flow Summary for NCAA Wrestling Tournament Tracker

Here's a comprehensive summary of your data flow from source to each dataframe, which will help you understand the system for future maintenance.

## Data Sources & Manual Inputs

1. **wrestling_results.txt**
   - Primary data source containing match results
   - **Requires manual updates** during tournament
   - Contains round information, wrestler names, schools, match outcomes

2. **ncaa_wrestling_draft.csv**
   - Contains fantasy draft information
   - Maps wrestlers to team owners
   - **Requires manual setup** before tournament

3. **Config Settings**
   - `PROBLEM_WRESTLERS` list - Needs manual updating when name conflicts arise
   - Placement point values - Point system configuration

## Data Processing Flow

```
wrestling_results.txt ──┐
                        │
ncaa_wrestling_draft.csv┼──► parse_wrestling_results() ──┬──► results_df
                        │                                │
config settings ────────┘                                ├──► round_df
                                                         │
                                                         └──► placements_df
                                                                 │
                                                                 ▼
                                                        calculate_team_points()
                                                                 │
                                                                 ▼
                                                            team_summary
```

## Detailed Data Flow Steps

1. **Initial Setup**
   - `setup_config_paths()` - Sets file paths for data sources
   - Load `ncaa_wrestling_draft.csv` to identify drafted wrestlers

2. **Main Processing** (`parse_wrestling_results()`)
   - Read tournament results from `wrestling_results.txt`
   - Create lookup dictionaries for wrestlers
   - First pass: identify placements and problematic matches
   - Second pass: process match results and calculate points
   - Track win types, rounds, and special cases
   - Calculate points for wins, advancements, and bonuses

3. **Data Transformation**
   - Convert dictionaries to pandas DataFrames
   - Sort and organize data
   - Apply placement points

4. **Final Calculations** (`calculate_team_points()`)
   - Aggregate results by team owner
   - Calculate total points by category (advancement, bonus, placement)
   - Create team summary statistics

## Key Dataframes & Their Relationships

1. **`results_df`** - Individual Wrestler Results
   - **Indexed by:** Wrestler name with school
   - **Contains:** Points, wins, placements, match details
   - **Dependencies:** Directly built from match parsing
   - **Used for:** Calculating team points, wrestler details view

2. **`round_df`** - Round-by-Round Results
   - **Indexed by:** Wrestler ID
   - **Contains:** Match outcomes by tournament round
   - **Dependencies:** Built from round information in match results
   - **Used for:** Round-by-round view, tracking tournament progress

3. **`placements_df`** - Final Placements
   - **Indexed by:** Wrestler ID
   - **Contains:** Weight class, placement information
   - **Dependencies:** Built from placement matches and explicit placement lines
   - **Used for:** Placement view, calculating placement points

4. **`team_summary`** - Team Performance
   - **Indexed by:** Team owner
   - **Contains:** Aggregate point totals, breakdowns by type
   - **Dependencies:** Calculated from `results_df`
   - **Used for:** Team standings, analytics views

## Why Manual Updates Matter

1. **Tournament Progress Tracking**
   - The `wrestling_results.txt` file needs regular updates during the tournament
   - Each update adds new match results that flow through the entire system
   - Without updates, points and standings will not reflect current tournament state

2. **Name Conflict Resolution**
   - Wrestlers with the same name require manual identification in `PROBLEM_WRESTLERS`
   - School abbreviations and name variations need normalization

3. **Configuration Adjustments**
   - Point values for placements may need updating based on tournament rules
   - Round naming in `ROUND_MAPPING` must match the format in result files

## Maintenance Considerations

1. **Data Validation**
   - Check that each update includes complete rounds
   - Verify that problematic wrestler matches are parsed correctly
   - Confirm no duplicate entries exist

2. **Troubleshooting Missing Data**
   - Missing rounds often indicate format mismatches between source and parsing
   - Check the `ROUND_MAPPING` dictionary against actual round names in the file
   - Verify regex patterns are capturing all match types

3. **Testing Updates**
   - After updating `wrestling_results.txt`, verify new data appears in app
   - Check total points calculations match expected values
   - Confirm new placement information is correctly processed

This summary should help you maintain and troubleshoot the application as tournament data evolves.