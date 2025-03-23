import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime
import pytz  # Import pytz for timezone handling

# Add the current directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from your package
from ncaa_wrestling_tracker.main import main
from ncaa_wrestling_tracker.processors.scorer import calculate_team_points
from ncaa_wrestling_tracker import config

# Update config paths to use the repository's Data folder
def setup_config_paths():
    # Get the repository root path
    repo_root = os.path.dirname(os.path.abspath(__file__))
    
    # Update config paths
    config.BASE_PATH = repo_root
    config.DATA_PATH = os.path.join(repo_root, "Data")
    config.RESULTS_FILE = os.path.join(config.DATA_PATH, "wrestling_results.txt")
    config.DRAFT_CSV = os.path.join(config.DATA_PATH, "ncaa_wrestling_draft.csv")
    config.OUTPUT_DIR = os.path.join(repo_root, "Results")
    
    # Ensure the output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

# Call the setup function
setup_config_paths()

# Set page configuration
st.set_page_config(
    page_title="NCAA Wrestling Draft Tracker", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed
)

# Get current time in EST timezone
eastern = pytz.timezone('US/Eastern')
est_time = datetime.now(eastern)
formatted_time = est_time.strftime("%m/%d/%Y %I:%M:%S %p EST")  # 12-hour format with AM/PM

# Page header
st.title("Fantasy Draft Tracker for NCAA Wrestling Championships")
st.markdown(f"Last updated: {formatted_time}")

# Simplified sidebar
st.sidebar.title("Fantasy Draft Tracker")

# Simple controls only
st.sidebar.subheader("Controls")
update_button = st.sidebar.button("Update Results")

# Optional: Add a simple about section
st.sidebar.markdown("---")
st.sidebar.markdown("Track NCAA Wrestling Tournament results for fantasy drafts")

# Function to load or process data
def load_or_process_data():
    if update_button or 'results_df' not in st.session_state:
        with st.spinner("Loading tournament results..."):
            try:
                # Run the main function from your package
                results_df, round_df, placements_df = main(return_results=True)
                
                # Only show an error if explicitly updating
                if 'champ_wins' not in results_df.columns and update_button:
                    st.warning("Data missing expected columns")
                
                team_summary = calculate_team_points(results_df)
                
                # Save to session state
                st.session_state['results_df'] = results_df
                st.session_state['round_df'] = round_df
                st.session_state['placements_df'] = placements_df
                st.session_state['team_summary'] = team_summary
                
                # Only show success message if explicitly updating
                if update_button:
                    st.success("Results updated successfully!")
            except Exception as e:
                # Only show error if explicitly updating
                if update_button:
                    st.error(f"Error processing results: {e}")
                    
                # Create empty DataFrames if needed
                if 'results_df' not in st.session_state:
                    st.session_state['results_df'] = pd.DataFrame()
                    st.session_state['round_df'] = pd.DataFrame()
                    st.session_state['team_summary'] = pd.DataFrame()
                    st.session_state['placements_df'] = pd.DataFrame()

# Load the data
load_or_process_data()

# Create tabs for different views
tabs = st.tabs(["Team Standings", "Round-by-Round", "Wrestler Details", "Placements", "Analytics (Beta)"])

with tabs[0]:
    st.header("Team Standings")
    if 'team_summary' in st.session_state and not st.session_state['team_summary'].empty:
        # Display the team standings table
        team_df = st.session_state['team_summary'].copy()
        team_df = team_df.reset_index(drop=True)
        team_df.index = team_df.index + 1  # Start rank at 1
        
        # Format columns for display
        display_df = team_df.copy()
        display_cols = ['owner', 'total_points', 'total_advancement', 'total_bonus', 'placement_points']
        display_cols = [col for col in display_cols if col in display_df.columns]
        display_df = display_df[display_cols]
        
        # Rename columns for display
        display_df.columns = ['Team', 'Total Points', 'Advancement Points', 'Bonus Points', 
                            'Placement Points' if 'placement_points' in display_cols else '']
        
        # Create horizontal bar chart of total points - moved from Enhanced Rankings
        team_df_sorted = team_df.sort_values('total_points', ascending=False)
        bar_fig = px.bar(
            team_df_sorted, 
            y='owner', 
            x='total_points',
            orientation='h',
            color='total_points',
            color_continuous_scale='Viridis',
            text='total_points',
            labels={
                'owner': 'Team',
                'total_points': 'Total Points'
            }
        )
        
        bar_fig.update_layout(
            title='Team Rankings by Total Points',
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        
        # Display chart and table side by side
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(bar_fig, use_container_width=True)
        
        with col2:
            # Make the table more visible - adjust height to show all rows
            st.dataframe(display_df, use_container_width=True, height=max(125, len(display_df) * 35 + 38))
    else:
        st.info("No team standings data available. Please update results.")

with tabs[1]:
    st.header("Round-by-Round Results")
    if 'round_df' in st.session_state and not st.session_state['round_df'].empty:
        round_df = st.session_state['round_df']
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            weight_classes = ['All'] + sorted(round_df['Weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes)
        
        with col2:
            teams = ['All'] + sorted(round_df['Owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams)
        
        # Apply filters
        filtered_df = round_df.copy()
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['Weight'] == selected_weight]
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['Owner'] == selected_team]
        
        # Format the dataframe - highlight wins and losses
        def highlight_results(val):
            if pd.isna(val):
                return ''
            elif isinstance(val, str) and val.startswith('W'):
                return 'background-color: #c6efce; color: #006100'  # Green for wins
            elif isinstance(val, str) and val.startswith('L'):
                return 'background-color: #ffc7ce; color: #9c0006'  # Red for losses
            return ''
        
        # Apply styling and display
        st.dataframe(filtered_df.style.applymap(highlight_results), use_container_width=True)
    else:
        st.info("No round-by-round data available. Please update results.")

with tabs[2]:
    st.header("Wrestler Details")
    if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
        results_df = st.session_state['results_df']
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            teams = ['All'] + sorted(results_df['owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams, key="wrestler_team")
        
        with col2:
            weight_classes = ['All'] + sorted(results_df['weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes, key="wrestler_weight")
        
        # Apply filters
        filtered_df = results_df.copy()
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['owner'] == selected_team]
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['weight'] == selected_weight]
        
        # Reorder and select columns for display
        cols_to_display = ['Wrestler', 'weight', 'seed', 'owner', 
                          'champ_wins', 'champ_advancement', 'champ_bonus',
                          'cons_wins', 'cons_advancement', 'cons_bonus', 
                          'placement', 'placement_points', 'total_points']
        cols_to_display = [col for col in cols_to_display if col in filtered_df.columns]
        
        # Rename columns for better display
        display_df = filtered_df[cols_to_display].copy()
        display_df = display_df.rename(columns={
            'Wrestler': 'Wrestler',
            'weight': 'Weight',
            'seed': 'Seed',
            'owner': 'Team',
            'champ_wins': 'Champ Wins',
            'champ_advancement': 'Champ Adv Pts',
            'champ_bonus': 'Champ Bonus Pts',
            'cons_wins': 'Cons Wins',
            'cons_advancement': 'Cons Adv Pts',
            'cons_bonus': 'Cons Bonus Pts',
            'placement': 'Placement',
            'placement_points': 'Place Pts',
            'total_points': 'Total Pts'
        })
        
        st.dataframe(display_df, use_container_width=True)
        
        # Show match details for selected wrestler
        if not filtered_df.empty:
            st.subheader("Match Details")
            wrestlers = filtered_df['Wrestler'].tolist()
            selected_wrestler = st.selectbox("Select Wrestler:", wrestlers)
            
            wrestler_row = filtered_df[filtered_df['Wrestler'] == selected_wrestler].iloc[0]
            if 'matches' in wrestler_row and wrestler_row['matches']:
                matches_data = []
                for match in wrestler_row['matches']:
                    matches_data.append({
                        'Round': match.get('round', ''),
                        'Opponent': match.get('opponent', ''),
                        'Result': match.get('result', ''),
                        'Type': match.get('win_type_full', ''),
                        'Advancement': match.get('advancement_points', 0),
                        'Bonus': match.get('bonus_points', 0),
                        'Total': match.get('total_points', 0)
                    })
                
                if matches_data:
                    st.dataframe(pd.DataFrame(matches_data))
                else:
                    st.info("No match details available for this wrestler.")
            else:
                st.info("No match details available for this wrestler.")
    else:
        st.info("No wrestler data available. Please update results.")

with tabs[3]:
    st.header("Placements")
    if 'placements_df' in st.session_state and not st.session_state['placements_df'].empty:
        placements_df = st.session_state['placements_df'].copy()
        
        # Analyze the column names in placements_df
        if st.checkbox("Show column debug info", key="debug_placement_cols", value=False):
            st.write(f"Columns in placements_df: {placements_df.columns.tolist()}")
            st.write(f"First few rows of placements_df:")
            st.write(placements_df.head())
        
        # Add owner information from results_df
        if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
            results_df = st.session_state['results_df'].copy()
            
            # Create a map from wrestler details to owner
            wrestler_to_owner = {}
            
            # Based on your data processing code, the key structure appears to be "name (school)"
            for _, row in results_df.iterrows():
                # Determine the wrestler identifier based on available columns
                if 'Wrestler' in results_df.columns:
                    wrestler_id = row['Wrestler']  # This is already in "name (school)" format in your case
                    wrestler_to_owner[wrestler_id] = row['owner']
            
            # Add owner column to placements_df
            if 'Wrestler ID' in placements_df.columns:
                placements_df['owner'] = placements_df['Wrestler ID'].map(wrestler_to_owner)
            elif 'name' in placements_df.columns and 'school' in placements_df.columns:
                # Create wrestler ID from separate name and school columns
                placements_df['wrestler_id'] = placements_df.apply(
                    lambda row: f"{row['name']} ({row['school']})", axis=1
                )
                placements_df['owner'] = placements_df['wrestler_id'].map(wrestler_to_owner)
        
        # Add filters - weight class and team owner
        col1, col2 = st.columns(2)
        with col1:
            weight_classes = ['All'] + sorted(placements_df['weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes, key="placement_weight")
        
        with col2:
            # Create owner filter if owner data is available
            if 'owner' in placements_df.columns and not placements_df['owner'].isna().all():
                team_owners = ['All'] + sorted(placements_df['owner'].dropna().unique().tolist())
                selected_owner = st.selectbox("Filter by Team Owner:", team_owners, key="placement_owner")
            else:
                st.info("Team owner information not available.")
                selected_owner = 'All'
        
        # Apply filters
        filtered_df = placements_df.copy()
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['weight'] == selected_weight]
        if selected_owner != 'All' and 'owner' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['owner'] == selected_owner]
        
        # Sort by placement
        if 'placement' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(['weight', 'placement'])
        
        # Display the dataframe
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No placement data available. Please wait for updated results.")

with tabs[4]:
    st.header("Advanced Analytics Dashboard")
    st.info("This dashboard is under development. New features will be added over time.")
    
    # Check if we have data
    if ('team_summary' not in st.session_state or 
        st.session_state['team_summary'].empty or 
        'results_df' not in st.session_state or 
        st.session_state['results_df'].empty):
        
        st.warning("No data available. Please update results to see analytics.")
    
    else:
        # We have data, proceed with visualizations
        analytics_tabs = st.tabs(["Points Breakdown", "Weight Class Analysis", "Efficiency Rankings"])
        
        # --------------------------------------------------
        # 1. Points Breakdown Visualization
        # --------------------------------------------------
        with analytics_tabs[0]:
            st.subheader("Team Points Breakdown")
            
            try:
                # Prepare data
                team_df = st.session_state['team_summary'].copy()
                
                # Ensure all columns exist, with defaults if missing
                if 'total_advancement' not in team_df.columns:
                    team_df['total_advancement'] = 0
                if 'total_bonus' not in team_df.columns:
                    team_df['total_bonus'] = 0
                if 'placement_points' not in team_df.columns:
                    team_df['placement_points'] = 0
                
                # Sort by total points
                team_df = team_df.sort_values('total_points', ascending=False)
                
                # Create a plotly stacked bar chart
                fig = go.Figure()
                
                # Add advancement points
                fig.add_trace(go.Bar(
                    name='Advancement',
                    x=team_df['owner'],
                    y=team_df['total_advancement'],
                    marker_color='#1f77b4',
                    text=team_df['total_advancement'].round(1),
                    textposition='auto'
                ))
                
                # Add bonus points
                fig.add_trace(go.Bar(
                    name='Bonus',
                    x=team_df['owner'],
                    y=team_df['total_bonus'],
                    marker_color='#ff7f0e',
                    text=team_df['total_bonus'].round(1),
                    textposition='auto'
                ))
                
                # Add placement points
                fig.add_trace(go.Bar(
                    name='Placement',
                    x=team_df['owner'],
                    y=team_df['placement_points'],
                    marker_color='#2ca02c',
                    text=team_df['placement_points'].round(1),
                    textposition='auto'
                ))
                
                # Update layout
                fig.update_layout(
                    barmode='stack',
                    title='Team Points by Category',
                    xaxis_title='Team',
                    yaxis_title='Points',
                    legend_title='Point Category',
                    height=500
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error creating Points Breakdown visualization: {e}")
                import traceback
                st.error(traceback.format_exc())
        
        # --------------------------------------------------
        # 2. Weight Class Heatmap
        # --------------------------------------------------
        with analytics_tabs[1]:
            st.subheader("Performance by Weight Class")
            
            try:
                # Prepare data
                results_df = st.session_state['results_df'].copy()
                
                # Create pivot table of points by team and weight class
                pivot_data = results_df.pivot_table(
                    values='total_points',
                    index='owner',
                    columns='weight',
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Ensure weight classes are in correct order
                weight_order = ['125', '133', '141', '149', '157', '165', '174', '184', '197', '285', 'DH']
                available_weights = [w for w in weight_order if w in pivot_data.columns]
                pivot_data = pivot_data[available_weights]
                
                # Sort teams by total points
                team_order = st.session_state['team_summary'].sort_values('total_points', ascending=False)['owner'].tolist()
                pivot_data = pivot_data.reindex(team_order)
                
                # Create text matrix with formatted integers
                text_matrix = []
                for i in range(len(pivot_data.index)):
                    text_row = []
                    for j in range(len(pivot_data.columns)):
                        text_row.append(str(int(pivot_data.iloc[i, j])))
                    text_matrix.append(text_row)
                
                # Create text color matrix
                text_color_matrix = []
                for i in range(len(pivot_data.index)):
                    color_row = []
                    for j in range(len(pivot_data.columns)):
                        value = pivot_data.iloc[i, j]
                        color_row.append("white" if value == 0 or value >= 15 else "black")
                    text_color_matrix.append(color_row)
                
                # Create the heatmap with built-in text template
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    colorscale=[
                        [0, 'rgb(220, 53, 69)'],         # Red for zero
                        [0.001, 'rgb(255, 255, 224)'],   # Light yellow
                        [0.3, 'rgb(173, 216, 230)'],     # Light blue
                        [0.6, 'rgb(102, 204, 255)'],     # Medium blue
                        [1, 'rgb(0, 0, 128)']            # Navy blue
                    ],
                    showscale=True,
                    zmin=0,
                    text=text_matrix,
                    texttemplate="%{text}",
                    textfont={"size": 12}
                ))
                
                # Configure layout
                fig.update_layout(
                    title="Points by Team and Weight Class",
                    height=600,
                    xaxis=dict(
                        title="Weight Class",
                        side="bottom"
                    ),
                    yaxis=dict(
                        title="Team",
                        autorange="reversed"
                    )
                )
                
                # Display the heatmap
                st.plotly_chart(fig, use_container_width=True)
                
                # Add an alternative visualization: radar chart for selected teams
                st.subheader("Weight Class Distribution by Team")
                
                # Team selection for radar chart
                selected_teams = st.multiselect(
                    "Select teams to compare:",
                    options=pivot_data.index.tolist(),
                    default=pivot_data.index.tolist()[:min(3, len(pivot_data.index))]
                )
                
                if selected_teams:
                    # Create radar chart
                    fig = go.Figure()
                    
                    for team in selected_teams:
                        fig.add_trace(go.Scatterpolar(
                            r=pivot_data.loc[team].values,
                            theta=pivot_data.columns,
                            fill='toself',
                            name=team
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True
                            )
                        ),
                        showlegend=True,
                        title="Points Distribution Across Weight Classes"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating Weight Class Analysis visualization: {e}")
                import traceback
                st.error(traceback.format_exc())
        
        # --------------------------------------------------
        # 3. Efficiency Rankings (renamed from Enhanced Rankings)
        # --------------------------------------------------
        with analytics_tabs[2]:
            st.subheader("Efficiency Rankings")
            
            try:
                # Prepare data
                team_df = st.session_state['team_summary'].copy()
                results_df = st.session_state['results_df'].copy()
                
                # Calculate additional metrics
                
                # 1. Points per wrestler
                team_df['Wrestlers with Points'] = team_df.get('Wrestlers with Points', pd.Series([0] * len(team_df)))
                team_df['Pts per Wrestler'] = (team_df['total_points'] / team_df['Wrestlers with Points']).fillna(0).round(2)
                
                # 2. Bonus point efficiency (% of points from bonus)
                team_df['Bonus %'] = (team_df['total_bonus'] / team_df['total_points'] * 100).fillna(0).round(1)
                
                # 3. Calculate All-Americans (wrestlers who placed in top 8)
                if 'placement' in results_df.columns:
                    all_americans = results_df[results_df['placement'].notna()].groupby('owner').size()
                    team_df['All-Americans'] = team_df.index.map(lambda x: all_americans.get(x, 0) if x in all_americans.index else 0)
                else:
                    team_df['All-Americans'] = 0
                
                # Add visualization of points per wrestler
                st.subheader("Efficiency Metrics")
                
                # Create bubble chart: x=Pts per Wrestler, y=Bonus %, size=Total Points
                if 'Pts per Wrestler' in team_df.columns and 'Bonus %' in team_df.columns:
                    bubble_fig = px.scatter(
                        team_df,
                        x='Pts per Wrestler',
                        y='Bonus %',
                        size='total_points',
                        color='owner',
                        hover_name='owner',
                        text='owner',
                        size_max=50,
                        title='Team Efficiency: Points per Wrestler vs Bonus Point %',
                        labels={
                            'Pts per Wrestler': 'Points per Wrestler',
                            'Bonus %': 'Bonus Point Percentage',
                            'owner': 'Team'
                        }
                    )
                    
                    bubble_fig.update_traces(
                        textposition='top center',
                        marker=dict(sizemin=5)
                    )
                    
                    bubble_fig.update_layout(
                        xaxis_title='Points per Wrestler',
                        yaxis_title='Bonus Point Percentage',
                        height=500
                    )
                    
                    st.plotly_chart(bubble_fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating Efficiency Rankings visualization: {e}")
                import traceback
                st.error(traceback.format_exc())

            # Add this to your Efficiency Rankings section
            # Under the bubble chart for efficiency metrics

            # Helper function for ordinal suffixes
            def get_placement_suffix(n):
                if 10 <= n % 100 <= 20:
                    return 'th'
                else:
                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
                return suffix

            st.subheader("All-Americans by Team")

            try:
                # Prepare data for All-Americans distribution
                if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
                    results_df = st.session_state['results_df'].copy()
                    
                    # Count All-Americans (wrestlers who placed in top 8) by team
                    if 'placement' in results_df.columns:
                        # Filter to only include wrestlers who placed in top 8
                        all_americans_df = results_df[
                            results_df['placement'].notna() & 
                            (results_df['placement'] <= 8)
                        ]
                        
                        # Create a categorical placement column
                        def get_placement_category(placement):
                            if placement == 1:
                                return "Champion (1st)"
                            elif placement == 2:
                                return "Runner-up (2nd)"
                            elif placement == 3:
                                return "Third Place (3rd)"
                            elif placement <= 8:
                                return f"Placed ({int(placement)}th)"
                            else:
                                return "Other"
                        
                        all_americans_df['placement_category'] = all_americans_df['placement'].apply(get_placement_category)
                        
                        # Define the order for placement categories
                        placement_order = ["Champion (1st)", "Runner-up (2nd)", "Third Place (3rd)", "Placed (4th)", 
                                        "Placed (5th)", "Placed (6th)", "Placed (7th)", "Placed (8th)"]
                        
                        # Add a constant column for counting
                        all_americans_df['count'] = 1
                        
                        # Sort weight classes for proper ordering within stacks
                        weight_order = ['125', '133', '141', '149', '157', '165', '174', '184', '197', '285']
                        all_americans_df['weight_order'] = all_americans_df['weight'].apply(
                            lambda w: weight_order.index(w) if w in weight_order else 999
                        )
                        all_americans_df = all_americans_df.sort_values(['owner', 'weight_order'])
                        
                        # Count All-Americans by team for sorting
                        aa_by_team = all_americans_df.groupby('owner').size().reset_index(name='total_aa')
                        aa_by_team = aa_by_team.sort_values('total_aa', ascending=False)
                        
                        # Create horizontal bar chart with color coding by placement
                        fig = px.bar(
                            all_americans_df,
                            y='owner',
                            x='count',  # Now using the count column
                            color='placement_category',
                            category_orders={
                                "owner": aa_by_team['owner'].tolist(),
                                "placement_category": placement_order
                            },
                            labels={
                                'owner': 'Team',
                                'count': 'All-Americans',
                                'placement_category': 'Placement'
                            },
                            title='All-Americans Distribution by Placement',
                            orientation='h',
                            hover_name='Wrestler',
                            hover_data={
                                'weight': True,
                                'placement': True,
                                'placement_category': False,
                                'owner': False,
                                'count': False
                            },
                            custom_data=['Wrestler', 'weight', 'placement']
                        )
                        
                        # Custom color scheme - gold, silver, bronze, and other colors for the rest
                        colors = {
                            "Champion (1st)": '#FFD700',     # Gold for champions
                            "Runner-up (2nd)": '#C0C0C0',    # Silver for runners-up
                            "Third Place (3rd)": '#CD7F32',  # Bronze for third
                            "Placed (4th)": '#1E90FF',       # Blue for 4th
                            "Placed (5th)": '#32CD32',       # Green for 5th
                            "Placed (6th)": '#9370DB',       # Purple for 6th
                            "Placed (7th)": '#FF6347',       # Tomato for 7th
                            "Placed (8th)": '#20B2AA'        # Light sea green for 8th
                        }
                        
                        # Update the color for each trace
                        for i, trace in enumerate(fig.data):
                            if trace.name in colors:
                                fig.data[i].marker.color = colors[trace.name]
                        
                        # Update layout
                        fig.update_layout(
                            height=500,
                            barmode='stack',
                            yaxis={'categoryorder': 'total ascending'},
                            legend_title_text='Placement',
                            hovermode='closest'
                        )
                        
                        # Add annotations with total counts at the end of each bar
                        for team in aa_by_team['owner'].unique():
                            total = aa_by_team[aa_by_team['owner'] == team]['total_aa'].values[0]
                            fig.add_annotation(
                                x=total + 0.1,  # Position annotation just past the end of the bar
                                y=team,
                                text=f"{total}",
                                showarrow=False,
                                font=dict(size=12)
                            )
                        
                        # Improve hover template to show wrestler name, school, weight, and placement
                        for i, trace in enumerate(fig.data):
                            placement_text = trace.name
                            if "(" in placement_text and ")" in placement_text:
                                placement_str = placement_text.split('(')[1].split(')')[0]
                                placement_num = int(placement_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''))
                                suffix = get_placement_suffix(placement_num)
                                fig.data[i].hovertemplate = f'<b>%{{customdata[0]}}</b><br>Weight: %{{customdata[1]}}<br>Placement: {placement_num}{suffix}<extra></extra>'
                        
                        # Display the chart
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Option to show the raw data
                        if st.checkbox("Show All-Americans details"):
                            # Create a dataframe showing each All-American by team
                            aa_details = all_americans_df[['owner', 'Wrestler', 'weight', 'seed', 'placement']]
                            aa_details = aa_details.sort_values(['owner', 'weight'])
                            st.dataframe(aa_details, use_container_width=True)
                            
                    else:
                        st.info("Placement information not available in results.")
                else:
                    st.info("Results data not available.")
                    
            except Exception as e:
                st.error(f"Error creating All-Americans distribution chart: {e}")
                import traceback
                st.error(traceback.format_exc())


# Footer
st.markdown("---")
st.markdown("Currently in Development - Created by Demetri D'Orsaneo")