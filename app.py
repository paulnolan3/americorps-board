# app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # Clean list-style strings
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

    # Parse dates
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')

    return df

df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filters")
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect("Program State", options=state_options, default=state_options)

apply_soon = st.sidebar.checkbox("Apply soon", help="Deadline within the next two weeks")

# === Filtering ===
filtered = df[df['program_state'].isin(states)]
if apply_soon:
    today  = date.today()
    cutoff = today + timedelta(days=14)
    filtered = filtered[
        (filtered['accept_end'].dt.date >= today) &
        (filtered['accept_end'].dt.date <= cutoff)
    ]

# === CSS for cards ===
st.markdown("""
    <style>
      .card-container {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #fafafa;
      }
      .card-container h4 {
        margin: 0;
        margin-bottom: 8px;
      }
      .card-container p {
        margin: 4px 0;
      }
    </style>
""", unsafe_allow_html=True)

# Helper to format dates
def format_date(ts):
    if pd.isna(ts):
        return ""
    return ts.strftime("%B %-d, %Y")

# === Detail View ===
if st.session_state.get('selected_program'):
    prog = filtered.loc[filtered['listing_id'] == st.session_state.selected_program].iloc[0]
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
        start = format_date(row['accept_start'])
        end   = format_date(row['accept_end'])

        # Card
        st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
        st.markdown(f"### {row['program_name']}")
        st.markdown(f"**State:** {row['program_state'].title()}")
        # <-- label changed below -->
        st.markdown(f"**Accepting Applications:** {start} → {end}")
        if st.button("Learn more", key=f"learn_{row['listing_id']}"):
            st.session_state.selected_program = row['listing_id']
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

