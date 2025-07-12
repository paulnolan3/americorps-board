import ast
import pandas as pd
import streamlit as st
from datetime import datetime

# add this helper at the top of your file
def safe_literal(s):
    """Try ast.literal_eval on non-null strings, else return None."""
    if pd.isna(s) or not isinstance(s, str) or s.strip()=="":
        return None
    try:
        return ast.literal_eval(s)
    except Exception:
        return None

@st.cache_data
def load_data():
    df = pd.read_csv(
        'americorps_listings_extracted.csv',
        converters={
            'program_state':  safe_literal,
            'metro_area':     safe_literal,
            'program_type':   safe_literal,
            'service_areas':  safe_literal,
            'skills':         safe_literal,
            'work_schedule':  safe_literal,
            'languages':      safe_literal,
        }
    )
    # … the rest of your load_data as before …
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'], format='%m/%d/%Y', errors='coerce')
    return df

# Then the rest of your app code…
