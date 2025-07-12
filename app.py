import streamlit as st
import pandas as pd
from datetime import date, timedelta

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')

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

    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end'] = pd.to_datetime(df['accept_end'], format='%m/%d/%Y', errors='coerce')
    return df

df = load_data()

st.sidebar.header("Filters")
state_options = sorted(df['program_state'].unique())
states = st.sidebar.multiselect("State or Territory", options=state_options, default=[])

EDU_OPTIONS = [
    "Less than High school",
    "Technical school / apprenticeship / vocational",
    "High school diploma/GED",
    "Some college",
    "Associates degree (AA)",
    "College graduate",
    "Graduate degree (e.g. MA, PhD, MD, JD)"
]
educations = st.sidebar.multiselect("Education Level", options=EDU_OPTIONS, default=[])

WORK_OPTIONS = ["Full Time", "Part Time", "Summer"]
st.sidebar.markdown("**Work Schedule**")
selected_work = [opt for opt in WORK_OPTIONS if st.sidebar.checkbox(opt, value=True)]

st.sidebar.markdown("---")
apply_soon = st.sidebar.checkbox("Apply soon", help="Deadline within the next two weeks")

st.sidebar.markdown("---")
st.sidebar.markdown("This app is not an official government website nor endorsed by AmeriCorps. It is built with love by an AmeriCorps Alum to improve the search process.")

filtered = df.copy()
if states:
    filtered = filtered[filtered['program_state'].isin(states)]
if educations:
    filtered = filtered[filtered['education_level'].isin(educations)]
if selected_work:
    filtered = filtered[filtered['work_schedule'].isin(selected_work)]
if apply_soon:
    today, cutoff = date.today(), date.today() + timedelta(days=14)
    filtered = filtered[(filtered['accept_end'].dt.date >= today) & (filtered['accept_end'].dt.date <= cutoff)]

def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

if st.session_state.get('selected_program'):
    prog = filtered.loc[filtered['listing_id'] == st.session_state.selected_program].iloc[0]

    if st.button("\u25c0 Back to overview"):
        st.session_state.selected_program = None

    st.title(prog['program_name'])

    digest = prog.get('digest_summary', "This is a sample summary generated from the full description.")
    st.markdown(f"### \ud83d\udcac {digest}")

    st.markdown(f"""
    **\ud83d\udccd Location**: {prog['program_state']}  
    **\ud83d\udcc5 Dates**: {format_date(prog['accept_start'])} – {format_date(prog['accept_end'])}  
    **\ud83d\udcbc Schedule**: {prog['work_schedule']}  
    **\ud83c\udf93 Education**: {prog['education_level']}  
    **\ud83e\uddc3 Age**: {int(prog['age_minimum'])}+  
    **\ud83d\udccb Program Type**: {prog['program_type']}
    """)

    tabs = st.tabs(["\ud83d\udcdd Overview", "\ud83d\udcaa Duties", "\ud83d\udcb0 Benefits", "\ud83e\udde0 Terms", "\ud83d\udcda Skills", "\ud83c\udf0d Service Areas", "\u2709\ufe0f Contact"])

    with tabs[0]:
        st.markdown(prog.get("program_description", "No description available."))
    with tabs[1]:
        st.markdown(prog.get("member_duties", "No duties listed."))
    with tabs[2]:
        st.markdown("\n".join(f"- {b}" for b in str(prog.get("program_benefits", "")).split(", ")))
    with tabs[3]:
        st.markdown("\n".join(f"- {t}" for t in str(prog.get("terms", "")).split(", ")))
    with tabs[4]:
        st.markdown("\n".join(f"- {s}" for s in str(prog.get("skills", "")).split(", ")))
    with tabs[5]:
        st.markdown("\n".join(f"- {s}" for s in str(prog.get("service_areas", "")).split(", ")))
    with tabs[6]:
        st.markdown(f"""
        **Name**: {prog.get('contact_name', 'N/A')}  
        **Address**: {prog.get('contact_address', 'N/A')}  
        **Phone**: {prog.get('contact_phone', 'N/A')}  
        **Email**: {prog.get('contact_email', 'N/A')}
        """)

    st.markdown("---")
    st.button("\ud83d\ude80 Apply Now (Coming Soon)")

else:
    st.title("AmeriCorps Opportunities")
    search_query = st.text_input("\ud83d\udd0d Search opportunities")
    if search_query:
        filtered = filtered[filtered['program_name'].str.contains(search_query, case=False, na=False)]

    for _, row in filtered.iterrows():
        start = format_date(row['accept_start'])
        end = format_date(row['accept_end'])

        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {start} → {end}")
        if st.button("Learn more", key=row['listing_id']):
            st.session_state.selected_program = row['listing_id']
