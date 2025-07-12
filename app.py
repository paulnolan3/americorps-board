# app.py

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # Clean up list‐style strings into plain text
    for col in [
        'program_state',
        'program_type',
        'service_areas',
        'skills',
        'work_schedule',
        'languages'
    ]:
        df[col] = (
            df[col]
            .fillna("")                   
            .astype(str)                  
            .str.replace(r"[\[\]']", "", regex=True)
            .str.strip()
        )

    # parse dates
    df['accept_start'] = pd.to_datetime(df['accept_start'],
                                        format='%m/%d/%Y',
                                        errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],
                                        format='%m/%d/%Y',
                                        errors='coerce')
    return df

df = load_data()

# Sidebar filters (remove Metro Area)
st.sidebar.header("Filters")
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect(
    "Program State",
    options=state_options,
    default=state_options
)
date_range = st.sidebar.date_input(
    "Application Start Date Range",
    value=[df['accept_start'].min(), df['accept_start'].max()]
)

# Filter DataFrame
filtered = df[
    df['program_state'].isin(states) &
    (df['accept_start'] >= pd.to_datetime(date_range[0])) &
    (df['accept_start'] <= pd.to_datetime(date_range[1]))
]

# Helper to format dates
def fmt_dt(dt):
    if pd.isna(dt):
        return ""
    return dt.strftime("%B %-d, %Y")  # e.g. "March 7, 2025"

# Detail view
if st.session_state.get('selected_program'):
    prog = filtered.loc[
        filtered['listing_id'] == st.session_state.selected_program
    ].iloc[0]
    if st.button("◀ Back to overview"):
        st.session_state.selected_program = None

    st.header(prog['program_name'])
    for col in prog.index:
        val = prog[col]
        # format our t
