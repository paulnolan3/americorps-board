# app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')
    # Clean list-style strings
    for col in [
        'program_state','program_type','service_areas',
        'skills','work_schedule','languages'
    ]:
        df[col] = (
            df[col]
            .fillna("").astype(str)
            .str.replace(r"[\[\]']", "", regex=True)
            .str.strip()
        )
    # Parse dates
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filters")
states = st.sidebar.multiselect(
    "Program State",
    options=sorted(df['program_state'].unique()),
    default=sorted(df['program_state'].unique())
)
apply_soon = st.sidebar.checkbox("Apply soon", help="Deadline within the next two weeks")

# Filter
filtered = df[df['program_state'].isin(states)]
if apply_soon:
    today, cutoff = date.today(), date.today() + timedelta(days=14)
    filtered = filtered[
        (filtered['accept_end'].dt.date >= today) &
        (filtered['accept_end'].dt.date <= cutoff)
    ]

# CSS
st.markdown("""
<style>
.card-container {
  border:1px solid #ddd; border-radius:8px;
  padding:16px; margin-bottom:16px; background:#fafafa;
}
.card-container h4 { margin:0 0 8px 0; }
.card-container p { margin:4px 0; }
</style>
""", unsafe_allow_html=True)

def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

# Detail view
if st.session_state.get('selected_program'):
    prog = filtered.loc[filtered['listing_id']==st.session_state.selected_program].iloc[0]
    if st.button("◀ Back to overview"):
        st.session_state.selected_program = None
    st.header(prog['program_name'])
    for col in prog.index:
        val = prog[col]
        if col in ("accept_start","accept_end"):
            val = format_date(val)
        st.markdown(f"**{col.replace('_',' ').title()}:** {val}")

# Overview with Learn-more inside each card
else:
    st.title("AmeriCorps Opportunities")
    for _, row in filtered.iterrows():
        start, end = format_date(row['accept_start']), format_date(row['accept_end'])
        with st.form(key=f"form_{row['listing_id']}"):
            st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
            st.markdown(f"### {row['program_name']}")
            st.markdown(f"**State:** {row['program_state'].title()}")
            st.markdown(f"**Accepting Applications:** {start} → {end}")
            submitted = st.form_submit_button("Learn more")
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                st.session_state.selected_program = row['listing_id']
                st.experimental_rerun()
