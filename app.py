import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end'] = pd.to_datetime(df['accept_end'], format='%m/%d/%Y', errors='coerce')
    return df

df = load_data()

# Initialize session state for selected program
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None

# Sidebar filters
st.sidebar.header("Filters")
states = st.sidebar.multiselect(
    "Program State",
    options=sorted(df['program_state'].dropna().unique()),
    default=sorted(df['program_state'].dropna().unique())
)
metros = st.sidebar.multiselect(
    "Metro Area",
    options=sorted(df['metro_area'].dropna().unique()),
    default=sorted(df['metro_area'].dropna().unique())
)
date_range = st.sidebar.date_input(
    "Application Start Date Range",
    value=[df['accept_start'].min(), df['accept_start'].max()]
)

# Filter data
filtered = df[
    df['program_state'].isin(states) &
    df['metro_area'].isin(metros) &
    (df['accept_start'] >= pd.to_datetime(date_range[0])) &
    (df['accept_start'] <= pd.to_datetime(date_range[1]))
]

# Detail view
if st.session_state.selected_program:
    prog = filtered[filtered['listing_id'] == st.session_state.selected_program].iloc[0]
    st.button("◀ Back to overview", on_click=lambda: st.session_state.update(selected_program=None))
    st.header(prog['program_name'])
    for col in prog.index:
        st.markdown(f"**{col.replace('_', ' ').title()}:** {prog[col]}")
else:
    st.title("AmeriCorps Opportunities")
    for _, row in filtered.iterrows():
        st.subheader(row['program_name'])
        st.write(f"**State:** {row['program_state']}")
        if pd.notna(row['metro_area']):
            st.write(f"**Metro:** {row['metro_area']}")
        st.write(f"**Applications:** {row['accept_start'].date()} – {row['accept_end'].date()}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
