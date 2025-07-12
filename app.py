import streamlit as st
import pandas as pd
from datetime import date, timedelta

# 1) Ensure our navigation flag exists
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None

# 2) Pill CSS for Service Areas and Skills
st.markdown("""
<style>
  .pill {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 4px;
    background-color: #1550ed;  /* service areas color */
    color: white;
    border-radius: 10px;
    font-size: 0.9em;
  }
  .pill-skill {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 4px;
    background-color: #112542;  /* skills color */
    color: white;
    border-radius: 10px;
    font-size: 0.9em;
  }
</style>
""", unsafe_allow_html=True)

# 3) Mapping for hyperlinked Program Type
PROGRAM_TYPE_LINKS = {
    "AmeriCorps NCCC": "https://www.americorps.gov/serve/americorps/americorps-nccc",
    "AmeriCorps NCCC Team Leaders": "https://www.americorps.gov/serve/americorps/americorps-nccc",
    "AmeriCorps State / National": "https://www.americorps.gov/serve/americorps/americorps-state-national",
    "AmeriCorps VISTA": "https://www.americorps.gov/serve/americorps/americorps-vista",
    "AmeriCorps VISTA Leaders": "https://www.americorps.gov/serve/americorps/americorps-vista"
}

@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')
    # Clean up list‐style strings
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

states = st.sidebar.multiselect(
    "State or Territory",
    options=sorted(df['program_state'].unique()),
    default=[]
)

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

WORK_OPTIONS = ["Full Time", "Part Time", "Summer"]
st.sidebar.markdown("**Work Schedule**")
selected_work = [
    opt for opt in WORK_OPTIONS
    if st.sidebar.checkbox(opt, value=True)
]

st.sidebar.markdown("---")

apply_soon = st.sidebar.checkbox(
    "Apply soon",
    help="Deadline within the next two weeks"
)

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
    today = date.today()
    cutoff = today + timedelta(days=14)
    filtered = filtered[
        (filtered['accept_end'].dt.date >= today) &
        (filtered['accept_end'].dt.date <= cutoff)
    ]

def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

# Callback to select a program
def _select_program(pid):
    st.session_state.selected_program = pid

# Callback to clear selection
def _clear_selection():
    st.session_state.selected_program = None

# === Overview Page ===
if st.session_state.selected_program is None:
    st.title("AmeriCorps Opportunities")
    search_query = st.text_input("🔍 Search opportunities")
    if search_query:
        filtered = filtered[
            filtered['program_name']
                    .str.contains(search_query, case=False, na=False)
        ]
    for _, row in filtered.iterrows():
        start = format_date(row['accept_start'])
        end   = format_date(row['accept_end'])
        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {start} → {end}")
        st.button(
            "Learn more",
            key=f"learn_{row['listing_id']}",
            on_click=_select_program,
            args=(row['listing_id'],)
        )

# === Detail View with Tabs ===
else:
    prog = filtered.loc[
        filtered['listing_id'] == st.session_state.selected_program
    ].iloc[0]

    # Back button
    st.button(
        "◀ Back to overview",
        on_click=_clear_selection
    )

    st.header(prog['program_name'])

    # Summary card
    state = prog['program_state'].title()
    raw_metro = prog.get('metro_area', "")
    if pd.isna(raw_metro) or raw_metro == "":
        metro_clean = ""
    else:
        metro_clean = (
            str(raw_metro)
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .strip()
        )
    location = f"{state}, {metro_clean}" if metro_clean else state
    start    = format_date(prog['accept_start'])
    end      = format_date(prog['accept_end'])
    age      = f"{prog['age_minimum']}+" if prog['age_minimum'] else "None"

    # Hyperlinked Program Type
    pt = prog['program_type']
    pt_url = PROGRAM_TYPE_LINKS.get(pt)
    if pt_url:
        pt_html = f'<a href="{pt_url}" target="_blank">{pt}</a>'
    else:
        pt_html = pt

    st.markdown(f"""
    <div style="
        border:1px solid #ddd;
        border-radius:8px;
        padding:12px;
        background:#f9f9f9;
    ">
      <p><strong>🗺 Location:</strong> {location}</p>
      <p><strong>📅 Dates:</strong> {start} – {end}</p>
      <p><strong>💼 Schedule:</strong> {prog['work_schedule']}</p>
      <p><strong>🎓 Education:</strong> {prog['education_level']}</p>
      <p><strong>✅ Age:</strong> {age}</p>
      <p><strong>📋 Program Type:</strong> {pt_html}</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab_labels = [
        ("Overview", "💬"),
        ("Duties",    "🛠"),
        ("Benefits",  "💵"),
        ("Terms",     "☑️"),
        ("Skills",    "📚"),
        ("Service Areas", "🌐"),
        ("Contact",   "✉️"),
    ]
    tabs = st.tabs([f"{emoji} {label}" for label, emoji in tab_labels])

    # Overview
    with tabs[0]:
        st.write(prog.get('description', ''))
        st.write(f"**Listing ID:** {prog['listing_id']}")

            # 1) Build the URL dynamically from the listing_id
        url = (
            "https://my.americorps.gov/mp/listing/viewListing.do"
            f"?fromSearch=true&id={prog['listing_id']}"
        )
        # 2) Render it as a clickable button via HTML
        st.markdown(
            f'''
            <a href="{url}" target="_blank" style="text-decoration:none">
              <button style="
                background-color:#1550ed;
                color:white;
                padding:8px 16px;
                border:none;
                border-radius:4px;
                font-size:1em;
                cursor:pointer;
              ">
                📝 Apply Now
              </button>
            </a>
            ''',
            unsafe_allow_html=True
        )


    # Duties
    with tabs[1]:
        st.write(prog['member_duties'])

    # Benefits
    with tabs[2]:
        st.write(prog['program_benefits'])

    # Terms
    with tabs[3]:
        st.write(prog['terms'])

    # Skills as pills
    with tabs[4]:
        skills = prog['skills'].split(',')
        skills_html = "".join(
            f'<span class="pill-skill">{skill.strip()}</span>'
            for skill in skills if skill.strip()
        )
        st.markdown(skills_html, unsafe_allow_html=True)

    # Service Areas as pills
    with tabs[5]:
        areas = prog['service_areas'].split(',')
        pills_html = "".join(
            f'<span class="pill">{area.strip()}</span>'
            for area in areas if area.strip()
        )
        st.markdown(pills_html, unsafe_allow_html=True)

    # Contact
    with tabs[6]:
        st.text(prog['contact'])
