# app.py

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # Load raw CSV
    df = pd.read_csv('americorps_listings_extracted.csv')

    # 1) Clean up any “['...']” strings into plain text
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
            .fillna("")                       # no NaN
            .astype(str)                      # ensure string
            .str.replace(r"[\[\]']", "", regex=True)  # remove [, ], '
            .str.strip()
        )

    # 2) Parse application dates
    df['accept_start'] = pd.to_datetime(
        df['accept_start'],
        format='%m/%d/%Y',
        errors='coerce'
    )
    df['accept_end'] = pd.to_datetime(
        df['accept_end'],
        format='%m/%d/%Y',
        errors='coerce'
    )

    # 3) Add pure‐date columns for filtering
    df['accept_start_date'] = df['accept_start'].dt.date
    df['accept_end_date']   = df['accept_end'].dt.date

    return df

df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filters")

state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect(
    "Program State",
    options=state_options,
    default=state_options,
)

date_range = st.sidebar.date_input(
    "Application Start Date Range",
    value=[
        df['accept_start_date'].min(),
        df['accept_start_date'].max()
    ]
)

# === Filter Data ===
filtered = df[
    df['program_state'].isin(states) &
    (df['accept_start_date'] >= date_range[0]) &
    (df['accept_start_date'] <= date_range[1])
]

# Helper to format a pandas Timestamp as "Month Day, Year"
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
        # nicely format our dates
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
