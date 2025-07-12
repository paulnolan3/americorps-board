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

# State or Territory (multi-select, default empty = no filter)
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect(
    "State or Territory",
    options=state_options,
    default=[]
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
    default=[]
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

# Disclaimer
st.sidebar.markdown("---")
st.sidebar.markdown(
    "This app is not an official government website nor endorsed by AmeriCorps. "
    "It is built with love by an AmeriCorps Alum to improve the search process."
)

# === Apply Filters ===
filtered = df.copy()

if states:
    filtered = filtered[filtered['program_state'].isin(states)]

if educations:
    filtered = filtered[filtered['education_level'].isin(educations)]

if selected_work:
    filtered = filtered[filtered['work_schedule'].isin(selected_work)]

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

    # ←— Add this
    search_query = st.text_input("🔍 Search opportunities")

    # Apply text filter if non-empty
    if search_query:
        filtered = filtered[
            filtered['program_name']
                    .str.contains(search_query, case=False, na=False)
        ]

    # Now render
    for _, row in filtered.iterrows():
        start = format_date(row['accept_start'])
        end   = format_date(row['accept_end'])

        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {start} → {end}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
