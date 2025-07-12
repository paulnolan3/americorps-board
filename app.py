# app.py

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # Clean up list‐style strings into plain text
    for col in [
        'program_state',
        'metro_area',
        'program_type',
        'service_areas',
        'skills',
        'work_schedule',
        'languages'
    ]:
        df[col] = (
            df[col]
            .fillna("")                   # avoid NaN
            .astype(str)                  # ensure string
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

# Sidebar filters
st.sidebar.header("Filters")
state_options = sorted(df['program_state'].unique())
metro_options = sorted([m for m in df['metro_area'].unique() if m])

states = st.sidebar.multiselect(
    "Program State",
    options=state_options,
    default=state_options
)
metros = st.sidebar.multiselect(
    "Metro Area",
    options=metro_options,
    default=metro_options
)
date_range = st.sidebar.date_input(
    "Application Start Date Range",
    value=[df['accept_start'].min(), df['accept_start'].max()]
)

# Filter DataFrame
filtered = df[
    df['program_state'].isin(states) &
    df['metro_area'].isin(metros) &
    (df['accept_start'] >= pd.to_datetime(date_range[0])) &
    (df['accept_start'] <= pd.to_datetime(date_range[1]))
]

# Detail view
if 'selected_program' in st.session_state and st.session_state.selected_program:
    prog = filtered.loc[
        filtered['listing_id'] == st.session_state.selected_program
    ].iloc[0]
    if st.button("◀ Back to overview"):
        st.session_state.selected_program = None
    st.header(prog['program_name'])
    for col in prog.index:
        val = prog[col]
        if isinstance(val, str):
            st.markdown(f"**{col.replace('_',' ').title()}:** {val}")
        else:
            st.markdown(f"**{col.replace('_',' ').title()}:** {val}")
else:
    st.title("AmeriCorps Opportunities")
    for _, row in filtered.iterrows():
        st.subheader(row['program_name'])
        st.write(f"**State:** {row['program_state'].title()}")
        if row['metro_area']:
            st.write(f"**Metro:** {row['metro_area'].title()}")
        st.write(f"**Applications:** {row['accept_start'].date()} → {row['accept_end'].date()}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
