"""
Job Application Workflow Dashboard
Interactive Streamlit dashboard with Sankey diagram visualization
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_manager import DataManager
from datetime import datetime
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Job Application Workflow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def create_sankey_diagram(df):
    """
    Create Sankey diagram showing application pipeline flow:
    Applied → Recruiter Screen → Interview → Outcomes (Rejected/Ghosted/Dropped/Offer)
    """
    if df.empty or len(df) == 0:
        return None
    
    # Clean data
    df = df.copy()
    df['status'] = df['status'].fillna('Applied')
    
    # Define pipeline stages
    stages = ['Applied', 'Recruiter Screen', 'Interview']
    outcomes = ['Rejected', 'Ghosted', 'Dropped', 'Offer']
    
    # Normalize status values (handle variations)
    status_mapping = {
        'In Progress': 'Recruiter Screen',  # Map old status to new
        'Withdrawn': 'Dropped',
    }
    df['status'] = df['status'].replace(status_mapping)
    
    # Create node labels: stages + outcomes
    all_nodes = stages + outcomes
    node_labels = all_nodes
    
    # Create indices for nodes
    stage_indices = {stage: idx for idx, stage in enumerate(stages)}
    outcome_indices = {outcome: len(stages) + idx for idx, outcome in enumerate(outcomes)}
    
    # Track flows based on actual status
    # Count applications at each stage
    applied_count = len(df[df['status'] == 'Applied'])
    screen_count = len(df[df['status'] == 'Recruiter Screen'])
    interview_count = len(df[df['status'] == 'Interview'])
    
    # Count outcomes
    rejected_count = len(df[df['status'] == 'Rejected'])
    ghosted_count = len(df[df['status'] == 'Ghosted'])
    dropped_count = len(df[df['status'] == 'Dropped'])
    offer_count = len(df[df['status'] == 'Offer'])
    
    # Build flows based on actual data
    source = []
    target = []
    value = []
    
    # Calculate total applications
    total_apps = len(df)
    
    if total_apps == 0:
        return None
    
    # Stage 1 → Stage 2: Applied → Recruiter Screen
    # Show how many moved from Applied to Recruiter Screen
    if screen_count > 0:
        source.append(stage_indices['Applied'])
        target.append(stage_indices['Recruiter Screen'])
        value.append(screen_count)
    
    # Stage 2 → Stage 3: Recruiter Screen → Interview
    if interview_count > 0:
        source.append(stage_indices['Recruiter Screen'])
        target.append(stage_indices['Interview'])
        value.append(interview_count)
    
    # Stage 3 → Outcomes: Interview → Offer
    if offer_count > 0:
        source.append(stage_indices['Interview'])
        target.append(outcome_indices['Offer'])
        value.append(offer_count)
    
    # Stage 1 → Outcomes: Applied → Rejected/Ghosted/Dropped (early exits)
    # Applications can be rejected/ghosted/dropped immediately after applying
    # Show these flows from Applied stage
    if rejected_count > 0:
        source.append(stage_indices['Applied'])
        target.append(outcome_indices['Rejected'])
        value.append(rejected_count)
    
    if ghosted_count > 0:
        source.append(stage_indices['Applied'])
        target.append(outcome_indices['Ghosted'])
        value.append(ghosted_count)
    
    if dropped_count > 0:
        source.append(stage_indices['Applied'])
        target.append(outcome_indices['Dropped'])
        value.append(dropped_count)
    
    # Stage 2 → Outcomes: Recruiter Screen → Rejected/Ghosted/Dropped
    # Some applications get rejected/ghosted after recruiter screen
    # For visualization, we'll show these as additional flows from Recruiter Screen
    # (In reality, some outcomes come from Applied, some from Recruiter Screen)
    # Since we don't track which stage each outcome came from, we show both possibilities
    # The diagram will show that outcomes can come from multiple stages
    
    # Ensure we have flows to render
    # If no flows exist, we need to show the current state
    if len(source) == 0:
        # Check what stages/outcomes have applications
        if applied_count > 0:
            # Show applications at Applied stage flowing to next stage (to visualize current state)
            source.append(stage_indices['Applied'])
            target.append(stage_indices['Recruiter Screen'])
            value.append(applied_count)
        elif screen_count > 0:
            source.append(stage_indices['Recruiter Screen'])
            target.append(stage_indices['Interview'])
            value.append(screen_count)
        elif interview_count > 0:
            source.append(stage_indices['Interview'])
            target.append(outcome_indices['Offer'])
            value.append(interview_count)
        elif rejected_count > 0 or ghosted_count > 0 or dropped_count > 0 or offer_count > 0:
            # Show outcomes from Recruiter Screen
            if rejected_count > 0:
                source.append(stage_indices['Recruiter Screen'])
                target.append(outcome_indices['Rejected'])
                value.append(rejected_count)
        else:
            return None
    
    # Create color palette
    # Stages: light yellow-green to green progression
    stage_colors = ['#F7DC6F', '#98D8C8', '#4ECDC4']  # Applied, Recruiter Screen, Interview
    # Outcomes: red for negative, green for positive
    outcome_colors = ['#FF6B6B', '#FFA07A', '#FFB6C1', '#2ECC71']  # Rejected, Ghosted, Dropped, Offer
    
    # Assign colors to nodes
    node_colors = stage_colors + outcome_colors
    
    # Create link colors (gradient from source to target)
    link_colors = []
    for i, src_idx in enumerate(source):
        if src_idx < len(stages):
            # Link from a stage
            if target[i] < len(stages):
                # Stage to stage: green gradient
                link_colors.append('rgba(76, 205, 196, 0.6)')
            else:
                # Stage to outcome
                outcome_idx = target[i] - len(stages)
                if outcome_idx == 3:  # Offer
                    link_colors.append('rgba(46, 204, 113, 0.6)')  # Green
                else:
                    link_colors.append('rgba(255, 107, 107, 0.6)')  # Red
        else:
            link_colors.append('rgba(200, 200, 200, 0.6)')
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            hovertemplate='%{value} applications<extra></extra>',
        )
    )])
    
    fig.update_layout(
        title={
            'text': "Job Application Pipeline Flow",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        font_size=12,
        height=800,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_status_breakdown(df):
    """Create pie chart for status breakdown"""
    if df.empty:
        return None
    
    status_counts = df['status'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    )])
    
    fig.update_layout(
        title="Status Breakdown",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_company_chart(df):
    """Create bar chart for top companies"""
    if df.empty:
        return None
    
    company_counts = df['company'].value_counts().head(10)
    
    fig = go.Figure(data=[go.Bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        marker_color='#4ECDC4'
    )])
    
    fig.update_layout(
        title="Top Companies by Applications",
        xaxis_title="Number of Applications",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def get_last_run_timestamp():
    """Get the timestamp of the last email processing run"""
    try:
        last_run_file = os.path.join(os.path.dirname(__file__), '.last_run')
        if os.path.exists(last_run_file):
            with open(last_run_file, 'r') as f:
                timestamp_str = f.read().strip()
                try:
                    last_run = datetime.fromisoformat(timestamp_str)
                    return last_run
                except:
                    return None
    except:
        pass
    return None

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Job Application Workflow Dashboard</h1>', unsafe_allow_html=True)
    
    # Display last run timestamp in top right corner
    last_run = get_last_run_timestamp()
    if last_run:
        # Format timestamp
        time_ago = datetime.now() - last_run
        if time_ago.days > 0:
            time_str = f"{time_ago.days} day(s) ago"
        elif time_ago.seconds > 3600:
            hours = time_ago.seconds // 3600
            time_str = f"{hours} hour(s) ago"
        elif time_ago.seconds > 60:
            minutes = time_ago.seconds // 60
            time_str = f"{minutes} minute(s) ago"
        else:
            time_str = "Just now"
        
        # Display in top right corner
        st.markdown(f"""
        <div style="position: fixed; top: 10px; right: 10px; background-color: #f0f2f6; 
                    padding: 8px 12px; border-radius: 5px; font-size: 0.85rem; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 999;">
            <strong>Last Run:</strong> {last_run.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <small style="color: #666;">{time_str}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Load data from PostgreSQL database
    data_manager = DataManager()
    
    # Clear cache to ensure fresh data from database
    @st.cache_data(ttl=30)  # Cache for 30 seconds to balance freshness and performance
    def load_fresh_data():
        """Load fresh data from PostgreSQL database"""
        return data_manager.get_applications(), data_manager.get_statistics()
    
    df, stats = load_fresh_data()
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Controls")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Clear cache to force reload from PostgreSQL
            load_fresh_data.clear()
            st.rerun()
        
        st.caption("💾 Connected to PostgreSQL database")
        
        st.markdown("---")
        st.header("📊 Statistics")
        st.metric("Total Applications", stats['total'])
        
        if stats['by_status']:
            st.subheader("By Status")
            for status, count in stats['by_status'].items():
                st.metric(status, count)
        
        st.markdown("---")
        st.header("🔍 Filters")
        
        # Status filter
        if not df.empty and 'status' in df.columns:
            statuses = ['All'] + df['status'].unique().tolist()
            selected_status = st.selectbox("Filter by Status", statuses)
            if selected_status != 'All':
                df = df[df['status'] == selected_status]
        
        # Company filter
        if not df.empty and 'company' in df.columns:
            companies = ['All'] + sorted(df['company'].dropna().unique().tolist())
            selected_company = st.selectbox("Filter by Company", companies)
            if selected_company != 'All':
                df = df[df['company'] == selected_company]
    
    # Main content
    if df.empty:
        st.warning("No job application data found. Run `python process_emails.py` to process emails from Gmail.")
        st.info("💡 Tip: Make sure you've set up Gmail API credentials and run the email processor first.")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applications", len(df))
        
        with col2:
            unique_companies = df['company'].nunique() if 'company' in df.columns else 0
            st.metric("Unique Companies", unique_companies)
        
        with col3:
            unique_locations = df['location'].nunique() if 'location' in df.columns else 0
            st.metric("Unique Locations", unique_locations)
        
        with col4:
            in_progress = len(df[df['status'] == 'In Progress']) if 'status' in df.columns else 0
            st.metric("In Progress", in_progress)
        
        st.markdown("---")
        
        # Sankey diagram
        st.header("📈 Application Pipeline Flow")
        st.markdown("**Flow: Applied → Recruiter Screen → Interview → Outcomes (Rejected/Ghosted/Dropped/Offer)**")
        
        sankey_fig = create_sankey_diagram(df)
        if sankey_fig:
            st.plotly_chart(sankey_fig, use_container_width=True)
        else:
            st.warning("⚠️ **Sankey diagram cannot be created** - No flow data available.")
            st.info("""
            **To see the pipeline flow diagram, you need applications that have progressed through stages:**
            - Applications at 'Recruiter Screen', 'Interview', or outcome stages (Rejected/Ghosted/Dropped/Offer)
            - Currently, all applications appear to be at the 'Applied' stage
            
            **Next steps:**
            1. Process more emails that contain status updates (interviews, rejections, etc.)
            2. Or manually update application statuses in the database
            """)
            
            # Show current status breakdown
            if 'status' in df.columns:
                st.subheader("Current Status Distribution")
                status_counts = df['status'].value_counts()
                st.bar_chart(status_counts)
        
        st.markdown("---")
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            status_fig = create_status_breakdown(df)
            if status_fig:
                st.plotly_chart(status_fig, use_container_width=True)
        
        with col2:
            company_fig = create_company_chart(df)
            if company_fig:
                st.plotly_chart(company_fig, use_container_width=True)
        
        st.markdown("---")
        
        # Data table with editable status
        st.header("📋 Application Details")
        
        # Display columns selector
        if not df.empty:
            display_columns = st.multiselect(
                "Select columns to display",
                options=df.columns.tolist(),
                default=['date', 'job_title', 'company', 'location', 'status']
            )
            
            if display_columns:
                # Ensure email_id is available for status updates (even if not displayed)
                if 'email_id' not in display_columns:
                    display_df_with_id = df[display_columns + ['email_id']].copy()
                else:
                    display_df_with_id = df[display_columns].copy()
                
                # Sort dataframe
                display_df = display_df_with_id.sort_values('date', ascending=False) if 'date' in display_columns else display_df_with_id
                
                # Initialize session state for updates
                if 'status_updates' not in st.session_state:
                    st.session_state.status_updates = {}
                if 'location_updates' not in st.session_state:
                    st.session_state.location_updates = {}
                
                # Create editable table with status dropdowns and location text fields
                st.markdown("**💡 Use the dropdowns/text fields below to update application details, then click 'Save Changes'**")
                
                # Import status options from config
                from config import STATUSES
                
                # Create a form for status updates
                with st.form("status_update_form"):
                    # Create header row
                    num_cols = len(display_columns)
                    header_cols = st.columns(num_cols)
                    for i, col_name in enumerate(display_columns):
                        with header_cols[i]:
                            st.markdown(f"**{col_name.replace('_', ' ').title()}**")
                    
                    # Display each row with editable status
                    for idx, row in display_df.iterrows():
                        row_cols = st.columns(num_cols)
                        email_id = row.get('email_id', '')
                        
                        for i, col_name in enumerate(display_columns):
                            with row_cols[i]:
                                if col_name == 'status':
                                    # Editable status dropdown
                                    current_status = str(row.get('status', 'Applied'))
                                    try:
                                        current_index = STATUSES.index(current_status) if current_status in STATUSES else 0
                                    except ValueError:
                                        current_index = 0
                                    
                                    status_key = f"status_{email_id}_{idx}"
                                    new_status = st.selectbox(
                                        "",
                                        options=STATUSES,
                                        index=current_index,
                                        key=status_key,
                                        label_visibility="collapsed"
                                    )
                                    
                                    # Track changes
                                    if new_status != current_status:
                                        st.session_state.status_updates[email_id] = new_status
                                
                                elif col_name == 'location':
                                    # Editable location text field
                                    current_location = str(row.get('location', '')) if pd.notna(row.get('location')) else ''
                                    location_key = f"location_{email_id}_{idx}"
                                    new_location = st.text_input(
                                        "",
                                        value=current_location,
                                        key=location_key,
                                        label_visibility="collapsed",
                                        placeholder="Enter location..."
                                    )
                                    
                                    # Track changes (only if different and not empty)
                                    if new_location != current_location and new_location.strip():
                                        st.session_state.location_updates[email_id] = new_location.strip()
                                    elif new_location.strip() == '' and current_location:
                                        # Allow clearing location
                                        st.session_state.location_updates[email_id] = None
                                
                                else:
                                    # Display other columns as text
                                    value = row.get(col_name, 'N/A')
                                    if pd.notna(value):
                                        if col_name == 'date':
                                            st.text(str(value)[:10])
                                        elif col_name == 'email_id':
                                            st.text(str(value)[:20])
                                        else:
                                            st.text(str(value)[:40])
                                    else:
                                        st.text('N/A')
                    
                    # Submit button
                    submitted = st.form_submit_button("💾 Save Status Changes", use_container_width=True)
                    
                    if submitted:
                        update_count = 0
                        error_count = 0
                        updates_made = []
                        
                        # Update statuses
                        if st.session_state.status_updates:
                            for email_id, new_status in st.session_state.status_updates.items():
                                if data_manager.update_status(email_id, new_status):
                                    update_count += 1
                                    updates_made.append(f"Status for {email_id[:8]}...")
                                else:
                                    error_count += 1
                        
                        # Update locations
                        if st.session_state.location_updates:
                            for email_id, new_location in st.session_state.location_updates.items():
                                if data_manager.update_location(email_id, new_location):
                                    update_count += 1
                                    updates_made.append(f"Location for {email_id[:8]}...")
                                else:
                                    error_count += 1
                        
                        if update_count > 0:
                            st.success(f"✓ Successfully updated {update_count} field(s)!")
                            # Clear the updates and reload data
                            st.session_state.status_updates = {}
                            st.session_state.location_updates = {}
                            load_fresh_data.clear()  # Clear cache
                            st.rerun()
                        elif error_count > 0:
                            st.error(f"✗ Failed to update {error_count} field(s). Please try again.")
                        else:
                            st.info("ℹ️ No changes detected.")
                
                # Also show read-only dataframe view (without email_id if not selected)
                st.markdown("---")
                st.markdown("**📊 Full Table View (Read-only)**")
                read_only_df = display_df[display_columns] if 'email_id' not in display_columns else display_df[display_columns]
                st.dataframe(
                    read_only_df,
                    use_container_width=True,
                    height=400
                )
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"job_applications_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == '__main__':
    main()

