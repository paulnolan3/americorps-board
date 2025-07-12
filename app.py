# app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # Clean up list‐style strings
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

    # Parse date fields
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

# Program State (multi-select)
states = st.sidebar.multiselect(
    "Program State",
    options=sorted(df['program_state'].unique()),
    default=sorted(df['program_state'].unique())
)

# Education Level (multi-select, default empty = no filter)
EDU_OPTIONS = [
    "Less than High school",
    "Technical school / apprenticeship / vocational",
    "High school diploma/GED",
    "Some college",
    "Associates degree (AA)",
    "College graduate",
    "Graduate degree (e.g. MA, PhD, MD, JD)"
]
educations = st.sidebar.multiselect(
    "Education Level",
    options=EDU_OPTIONS,
    default=[]  # default to empty: show all
)

# Work Schedule (checkboxes)
WORK_OPTIONS = ["Full Time", "Part Time", "Summer"]
st.sidebar.markdown("**Work Schedule**")
selected_work = [
    opt for opt in WORK_OPTIONS
    if st.sidebar.checkbox(opt, value=True)
]

# Separator
st.sidebar.markdown("---")

# Apply Soon
apply_soon = st.sidebar.checkbox(
    "Apply soon",
    help="Deadline within the next two weeks"
)

# === Apply Filters ===
# Start with all rows
filtered = df.copy()

# Filter by state
if states:
    filtered = filtered[filtered['program_state'].isin(states)]

# Filter by education only if user selected any
if educations:
    filtered = filtered[filtered['education_level'].isin(educations)]

# Filter by work schedule
if selected_work:
    filtered = filtered[filtered['work_schedule'].isin(selected_work)]

# Filter by upcoming deadlines
if apply_soon:
    today, cutoff = date.today(), date.today() + timedelta(days=14)
    filtered = filtered[
        (filtered['accept_end'].dt.date >= today) &
        (filtered['accept_end'].dt.date <= cutoff)
    ]

# Helper to format dates
def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

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
        if col in ("age_minimum", "age_maximum") and pd.isna(val):
            val = "None"
        st.markdown(f"**{col.replace('_',' ').title()}:** {val}")

# === Overview Page ===
else:
    st.title("AmeriCorps Opportunities")
    for _, row in filtered.iterrows():
        start = format_date(row['accept_start'])
        end   = format_date(row['accept_end'])

        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {start} → {end}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
