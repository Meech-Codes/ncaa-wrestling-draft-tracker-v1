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
