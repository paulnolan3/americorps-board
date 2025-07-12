import ast
import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_data
def load_data():
    # use literal_eval to turn "['MAINE']" back into a Python list
    df = pd.read_csv(
        'americorps_listings_extracted.csv',
        converters={
            'program_state': ast.literal_eval,
            'metro_area':    ast.literal_eval,
            'program_type':  ast.literal_eval,
            'service_areas': ast.literal_eval,
            'skills':        ast.literal_eval,
            'work_schedule': ast.literal_eval,
            'languages':     ast.literal_eval
        }
    )
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'], format='%m/%d/%Y', errors='coerce')
    return df

def pretty_list(cell):
    """Join a list into a title-cased string, or return empty if None."""
    if isinstance(cell, list):
        return ", ".join(cell).title()
    return ""

df = load_data()

# Overview page
st.title("AmeriCorps Opportunities")
for _, row in df.iterrows():
    st.subheader(row['program_name'])
    # display program_state as clean text
    st.write(f"**State:** {pretty_list(row['program_state'])}")
    # metro (only if present)
    metro = pretty_list(row['metro_area'])
    if metro:
        st.write(f"**Metro:** {metro}")
    st.write(f"**Applications:** {row['accept_start'].date()} → {row['accept_end'].date()}")
    if st.button("Learn more", key=row['listing_id']):
        st.session_state.selected_program = row['listing_id']

# Detail view (as before)
if st.session_state.get('selected_program'):
    prog = df.loc[df['listing_id']==st.session_state.selected_program].iloc[0]
    st.button("◀ Back", on_click=lambda: st.session_state.update(selected_program=None))
    st.header(prog['program_name'])
    for col in prog.index:
        val = prog[col]
        if isinstance(val, list):
            val = ", ".join(val).title()
        st.markdown(f"**{col.replace('_',' ').title()}:** {val}")
