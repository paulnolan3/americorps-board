import streamlit as st
import pandas as pd
from datetime import date, timedelta

# === CSS Styling ===
st.markdown("""
<style>
  /* Pill for count display */
  .pill {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 6px 2px 0;
    background-color: #1550ed;
    color: white;
    border-radius: 9999px;
    font-size: 0.85em;
    cursor: default;
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

# === Session State ===
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'service_area_filters' not in st.session_state:
    st.session_state.service_area_filters = []

# === Constants ===
RESULTS_PER_PAGE = 20

# === Data Loader ===
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

# === Navigation Helpers ===
def select_program(pid):
    st.session_state.selected_program = pid
    st.session_state.scroll_to_top = True

def clear_selection():
    st.session_state.selected_program = None

def go_next():
    st.session_state.page_number += 1

def go_prev():
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1

# === Load Data ===
df = load_data()

# === Sidebar Filters ===
st.sidebar.header("Filters")
states = st.sidebar.multiselect("State or Territory", sorted(df['program_state'].unique()))
educations = st.sidebar.multiselect("Education Level", [
    "Less than High school", "Technical school / apprenticeship / vocational",
    "High school diploma/GED", "Some college", "Associates degree (AA)",
    "College graduate", "Graduate degree (e.g. MA, PhD, MD, JD)"
])
st.sidebar.markdown("**Work Schedule**")
selected_work = [opt for opt in ["Full Time", "Part Time", "Summer"] if st.sidebar.checkbox(opt, value=True)]
st.sidebar.markdown("---")
apply_soon = st.sidebar.toggle("Apply soon", help="Deadline in the next two weeks")
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
<span style='color: gray; font-size: 0.85em;'>
Disclaimer: This tool is not a government website or endorsed by AmeriCorps. This tool helps with search and discovery. All applications must be submitted through the official <a href='https://my.americorps.gov/mp/listing/publicRequestSearch.do' target='_blank' style='color: gray;'>MyAmeriCorps portal</a>.
</span>
""", unsafe_allow_html=True)

# === Main View ===
if st.session_state.selected_program is None:
    st.title("AmeriCorps Explorer")

    # Data filters
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
        filtered = filtered[(filtered['accept_end'].dt.date >= today) & (filtered['accept_end'].dt.date <= cutoff)]

    # Count
    st.markdown(f"### There are <span class='pill'>{len(filtered)}</span> opportunities to serve.", unsafe_allow_html=True)

    # Search
    search_query = st.text_input(
        "Search opportunities by name, service area, or skill",
        value=st.session_state.search_query,
        placeholder="community outreach, veterans, teaching"
    )
    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        st.session_state.page_number = 0
    if search_query:
        q = search_query.lower()
        filtered = filtered[filtered.apply(
            lambda r: any(q in str(r[f]).lower() for f in ['program_name','description','member_duties','program_benefits','skills','service_areas']), axis=1)
    ]

    # Service Area pills
    selected = st.pills(
        "Service Areas",
        ["Education","Environment","Health","Disaster Relief","Veterans"],
        selection_mode="multi",
        default=st.session_state.service_area_filters,
        key="service_area_filters",
    )
    if selected:
        filtered = filtered[filtered['service_areas'].apply(
            lambda cell: any(s in [x.strip() for x in cell.split(',')] for s in selected)
        )]

    # Pagination
    total = max(1,(len(filtered)-1)//RESULTS_PER_PAGE+1)
    start = st.session_state.page_number*RESULTS_PER_PAGE
    end = start+RESULTS_PER_PAGE
    page_data = filtered.iloc[start:end]

    # Listings
    for _,row in page_data.iterrows():
        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {format_date(row['accept_start'])} → {format_date(row['accept_end'])}")
        st.button("Learn more", key=f"learn_{row['listing_id']}", on_click=select_program, args=(row['listing_id'],))
        st.divider()

    # Nav
    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        if st.session_state.page_number>0: st.button("◀ Previous",on_click=go_prev)
    with c2:
        st.markdown(f"**Page {st.session_state.page_number+1} of {total}**")
    with c3:
        if st.session_state.page_number<total-1: st.button("Next ▶",on_click=go_next)

# Detail View
else:
    import streamlit.components.v1 as components
    components.html("""
<script>window.scrollTo(0,0);</script>
""" ,height=0,width=0)
    prog = df.loc[df['listing_id']==st.session_state.selected_program].iloc[0]
    st.button("◀ Back to search",on_click=clear_selection)

    col1,col2 = st.columns([1,1])
    with col1:
        st.header(prog['program_name'])
        link = f"https://my.americorps.gov/mp/listing/viewListing.do?fromSearch=true&id={prog['listing_id']}"
        st.markdown(f"<a href='{link}' target='_blank' class='apply-btn'>Apply Now</a>", unsafe_allow_html=True)
    with col2:
        loc = prog['program_state'].title()
        metro = str(prog['metro_area']).strip("[]'") if pd.notna(prog['metro_area']) else ""
        loc = f"{loc}, {metro}" if metro else loc
        st.markdown(
            f"<div class='summary-card'><h4 style='margin:0 0 8px;'>Program Summary</h4>"
            f"<p><strong>📍 Location:</strong> {loc}</p>"
            f"<p><strong>🗓️ Dates:</strong> {format_date(prog['accept_start'])} – {format_date(prog['accept_end'])}</p>"
            f"<p><strong>💼 Schedule:</strong> {prog['work_schedule']}</p>"
            f"<p><strong>🎓 Education:</strong> {prog['education_level']}</p>"
            f"<p><strong>✅ Age:</strong> {int(prog['age_minimum']) if pd.notna(prog['age_minimum']) else 'None'}+</p></div>"
        ,unsafe_allow_html=True)

    tabs = st.tabs(["💬 Overview","🛠 Duties","💵 Benefits","☑️ Terms","📚 Skills","🌐 Service Areas","✉️ Contact"])
    with tabs[0]:
        st.write(prog.get('description',''))
        st.write(f"**Listing ID:** {prog['listing_id']}")
    with tabs[1]:
        st.write(prog['member_duties'])
    with tabs[2]:
        st.write(prog['program_benefits'])
    with tabs[3]:
        st.write(prog['terms'] if pd.notna(prog['terms']) else 'None')
    with tabs[4]:
        skills_list = [s.strip() for s in prog['skills'].split(',') if s.strip()]
        if skills_list:
            cols = st.columns(len(skills_list))
            for idx, skill in enumerate(skills_list):
                cols[idx].badge(skill)
    with tabs[5]:
        areas_list = [a.strip() for a in prog['service_areas'].split(',') if a.strip()]
        if areas_list:
            cols2 = st.columns(len(areas_list))
            for idx, area in enumerate(areas_list):
                cols2[idx].badge(area)
    with tabs[6]:
        st.text(prog['contact'])
