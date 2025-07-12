import streamlit as st
import pandas as pd
from datetime import date, timedelta

# === CSS for pills, Apply button, and summary card ===
st.markdown("""
<style>
  .pill {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 4px;
    background-color: #1550ed;
    color: white;
    border-radius: 10px;
    font-size: 0.9em;
  }
  .pill-skill {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 4px;
    background-color: #112542;
    color: white;
    border-radius: 10px;
    font-size: 0.9em;
  }
  .apply-btn {
    border: 2px solid #1550ed;
    background-color: transparent;
    color: #1550ed;
    padding: 8px 16px;
    border-radius: 9999px;
    font-size: 1em;
    transition: background-color 0.2s, color 0.2s;
    text-decoration: none !important;
    cursor: pointer;
  }
  .apply-btn:hover {
    background-color: #1550ed;
    color: white;
  }
  .summary-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    background: #f9f9f9;
    margin-bottom: 24px;
  }
</style>
""", unsafe_allow_html=True)

# === Session state for navigation ===
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None

# === Helpers ===
@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')
    for col in ['program_state','program_type','service_areas','skills','work_schedule','languages']:
        df[col] = (
            df[col].fillna("")
                  .astype(str)
                  .str.replace(r"[\[\]']", "", regex=True)
                  .str.strip()
        )
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')
    return df

def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

def select_program(pid):
    st.session_state.selected_program = pid

def clear_selection():
    st.session_state.selected_program = None

df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filters")
states = st.sidebar.multiselect("State or Territory", sorted(df['program_state'].unique()))
EDU_OPTIONS = [
    "Less than High school",
    "Technical school / apprenticeship / vocational",
    "High school diploma/GED",
    "Some college",
    "Associates degree (AA)",
    "College graduate",
    "Graduate degree (e.g. MA, PhD, MD, JD)"
]
educations = st.sidebar.multiselect("Education Level", EDU_OPTIONS)
WORK_OPTIONS = ["Full Time", "Part Time", "Summer"]
st.sidebar.markdown("**Work Schedule**")
selected_work = [opt for opt in WORK_OPTIONS if st.sidebar.checkbox(opt, value=True)]
st.sidebar.markdown("---")
apply_soon = st.sidebar.checkbox("Apply soon", help="Deadline within the next two weeks")
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

# === Overview View ===
if st.session_state.selected_program is None:
    st.title("AmeriCorps Opportunities")
    search_query = st.text_input("🔍 Search opportunities")
    if search_query:
        filtered = filtered[
            filtered['program_name'].str.contains(search_query, case=False, na=False)
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
            on_click=select_program,
            args=(row['listing_id'],)
        )
        st.divider()

# === Detail View ===
else:
    prog = filtered.loc[filtered['listing_id'] == st.session_state.selected_program].iloc[0]
    st.button("◀ Back to search", on_click=clear_selection)

    # === Two equal columns ===
    col1, col2 = st.columns(2)
    with col1:
        st.header(prog['program_name'])
        url = (
            "https://my.americorps.gov/mp/listing/viewListing.do"
            f"?fromSearch=true&id={prog['listing_id']}"
        )
        st.markdown(
            f'<a href="{url}" target="_blank" class="apply-btn">Apply Now</a>',
            unsafe_allow_html=True
        )
        # extra gap below Apply button
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    with col2:
        state       = prog['program_state'].title()
        raw_metro   = prog.get('metro_area', "")
        metro_clean = "" if not raw_metro or pd.isna(raw_metro) else str(raw_metro).strip("[]' ")
        location    = f"{state}, {metro_clean}" if metro_clean else state
        start       = format_date(prog['accept_start'])
        end         = format_date(prog['accept_end'])
        age         = f"{prog['age_minimum']}+" if prog['age_minimum'] else "None"

        st.markdown(f"""
        <div class="summary-card">
          <h4 style="margin:0 0 8px;">Program Summary</h4>
          <p style="margin:4px 0;"><strong>🗺 Location:</strong> {location}</p>
          <p style="margin:4px 0;"><strong>📅 Dates:</strong> {start} – {end}</p>
          <p style="margin:4px 0;"><strong>💼 Schedule:</strong> {prog['work_schedule']}</p>
          <p style="margin:4px 0;"><strong>🎓 Education:</strong> {prog['education_level']}</p>
          <p style="margin:4px 0;"><strong>✅ Age:</strong> {age}</p>
        </div>
        """, unsafe_allow_html=True)

    # === Small gap before tabs ===
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # === Full-width Tabs ===
    tabs = st.tabs([
        "💬 Overview", "🛠 Duties", "💵 Benefits", "☑️ Terms",
        "📚 Skills", "🌐 Service Areas", "✉️ Contact"
    ])

    with tabs[0]:
        st.write(prog.get('description', ''))
        st.write(f"**Listing ID:** {prog['listing_id']}")

    with tabs[1]:
        st.write(prog['member_duties'])

    with tabs[2]:
        st.write(prog['program_benefits'])

    with tabs[3]:
        st.write(prog['terms'])

    with tabs[4]:
        skills = [s.strip() for s in prog['skills'].split(',') if s.strip()]
        st.markdown(
            "".join(f'<span class="pill-skill">{s}</span>' for s in skills),
            unsafe_allow_html=True
        )

    with tabs[5]:
        areas = [a.strip() for a in prog['service_areas'].split(',') if a.strip()]
        st.markdown(
            "".join(f'<span class="pill">{a}</span>' for a in areas),
            unsafe_allow_html=True
        )

    with tabs[6]:
        st.text(prog['contact'])
