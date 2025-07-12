import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

    # ----- CLEAN UP list‐style strings into plain text -----
    # strip [, ], ' characters out of these columns
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
        )

    # parse dates
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')

    return df
