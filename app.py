# app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # clean up list‐style strings
    for col in [
        'program_state','program_type','service_areas',
        'skills','work_schedule','languages'
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

# === Sidebar Filters ===
st.sidebar.header("Filters")

# Program State (multi-select)
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect(
    "Program State",
    options=state_options,
    default=state_options
)

# Education Level (single-select)
EDU_OPTIONS = [
    "Less than High school",
    "Technical school / apprenticeship / vocational",
    "High school diploma/GED",
    "Some college",
    "Associates degree (AA)",
    "College graduate",
    "Graduate degree (e.g. MA, PhD, MD, JD)"
]
education = st.sidebar.selectbox(
    "Education Level",
    options=EDU_OPTIONS
)

# Work Schedule (checkboxes)
WORK_OPTIONS = ["Full Time", "Part Time", "Summer"]
selected_w_
