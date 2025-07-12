# app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # Clean up “['...']” strings into plain text
    list_cols = [
        'program_state',
        'program_type',
        'service_areas',
        'skills',
        'work_schedule',
        'languages'
    ]
    for col in list_cols:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.replace(r"[\[\]']", "", regex=True)
            .str.strip()
        )

    # Parse dates
    df['accept_start'] = pd.to_datetime(
        df['accept_start'], format='%m/%d/%Y', errors='coerce'
    )
    df['accept_end']   = pd.to_datetime(
        df['accept_end'],   format='%m/%d/%Y', errors='coerce'
    )

    return df

df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filters")

# State filter
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect(
    "Program State",
    options=state_options,
    default=state_options
)

# New: upcoming deadline filter
soon = st.sidebar.checkbox(
    "Application deadline soon",
    help="Deadline within the next two weeks"
)

# === Filter Data ===
filtered = df[df['program_state'].isin(states)]

if soon:
    today  = date.today()
    cutoff = today + timedelta(days=14)
    # keep only those with accept_end within [today, cutoff]
    filtered = filtered[
        (filtered['accept_end'].dt.date >= today) &
        (filtered['accept_end'].dt.date <= cutoff)
    ]

# Helper to format dates as "Month Day, Year"
def format_date(ts):
    if pd.isna(ts):
        return ""
    return ts.strftime("%B %-d, %Y")

# === Detail View ===
if st.session_state.get('selected_program'):
    prog = filtered.loc[
        filtered['listing_id'] == st.session_state.selected_program
    ].iloc[0]

    if st.button("◀ Back to overview"):
        st.session_state.selected_program = None

    st.header(prog['program_name'])
    for col in prog.index:
        val = prog[col]
        if col in ("accept_start", "accept_end"):
            val = format_date(val)
        st.markdown(f"**{col.replace('_',' ').title()}:** {val}")

# === Overview Page ===
else:
    st.title("AmeriCorps Opportunities")
    for _, row in filtered.iterrows():
        st.subheader(row['program_name'])
        st.write(f"**State:** {row['program_state'].title()}")
        start = format_date(row['accept_start'])
        end   = format_date(row['accept_end'])
        st.write(f"**Applications:** {start} → {end}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
