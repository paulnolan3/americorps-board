import streamlit as st
import pandas as pd
from datetime import date, timedelta

# === Unconditional Scroll-to-Top Injection ===
# This runs on every rerun (e.g., pagination or detail view), forcing the window to the top.
st.markdown(
    """
    <script>
      // Delay ensures execution after Streamlit's rerender
      setTimeout(function() {
        window.scrollTo(0, 0);
      }, 30);
    </script>
    """,
    unsafe_allow_html=True
)

# === CSS Styling ===
st.markdown("""
<style>
  .pill, .pill-filter {
    display: inline-block;
    padding: 4px 10px;
    margin: 2px 6px 2px 0;
    background-color: #1550ed;
    color: white;
    border-radius: 9999px;
    font-size: 0.85em;
    cursor: pointer;
  }
  .pill-skill {
    background-color: #112542;
    padding: 4px 10px;
    border-radius: 10px;
    color: white;
    margin: 2px 4px;
    font-size: 0.9em;
    display: inline-block;
    white-space: nowrap;
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
  .tutorial-box {
    background-color: #fffbea;
    border-left: 6px solid #f7c948;
    padding: 16px;
    margin: 16px 0;
    border-radius: 6px;
  }
</style>
""", unsafe_allow_html=True)

# === Session State Initialization ===
for key, default in [('selected_program', None), ('search_query', ''), ('page_number', 0), ('show_tutorial', True)]:
    if key not in st.session_state:
        st.session_state[key] = default

# === Constants ===
RESULTS_PER_PAGE = 20

# === Data Loader ===
@st.cache_data
def load_data():
    df = pd.read_csv('americorps_listings_extracted.csv')
    list_cols = ['program_state', 'program_type', 'service_areas', 'skills', 'work_schedule', 'languages']
    for col in list_cols:
        df[col] = (
            df[col].fillna("")
                  .astype(str)
                  .str.replace(r"[\[\]']", "", regex=True)
                  .str.strip()
        )
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')
    return df

# === Helper Functions ===
def format_date(ts):
    return "" if pd.isna(ts) else ts.strftime("%B %-d, %Y")

def select_program(pid):
    st.session_state.selected_program = pid

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
apply_soon = st.sidebar.checkbox("Apply soon", help="Deadline in the next two weeks")
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <span style='color: gray; font-size: 0.85em;'>
    Disclaimer: This is not a government site. Apply through <a href='https://my.americorps.gov/mp/listing/publicRequestSearch.do' target='_blank'>MyAmeriCorps</a>.
    </span>
    """, unsafe_allow_html=True)

# === Main vs Detail View ===
if st.session_state.selected_program is None:
    # --- Main View ---
    st.title("AmeriCorps Explorer")

    # Build filters
    apply_filters = any([states, educations, len(selected_work) < 3, apply_soon, st.session_state.search_query.strip()])
    if not apply_filters:
        df = df.sample(frac=1).reset_index(drop=True)
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

    st.markdown(f"### There are <span class='pill'>{len(filtered)}</span> opportunities.", unsafe_allow_html=True)
    search_input = st.text_input("Search by name, area, or skill", value=st.session_state.search_query)
    if search_input != st.session_state.search_query:
        st.session_state.search_query = search_input
        st.session_state.page_number = 0
    if st.session_state.search_query:
        q = st.session_state.search_query.lower()
        filtered = filtered[filtered.apply(lambda r: any(q in str(r[f]).lower() for f in ['program_name','description','member_duties','program_benefits','skills','service_areas']), axis=1)]

    # Pagination
    total_pages = max(1, (len(filtered)-1)//RESULTS_PER_PAGE + 1)
    start_idx = st.session_state.page_number * RESULTS_PER_PAGE
    end_idx = start_idx + RESULTS_PER_PAGE
    visible = filtered.iloc[start_idx:end_idx]

    for _, row in visible.iterrows():
        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting: {format_date(row['accept_start'])} → {format_date(row['accept_end'])}")
        st.button("Learn more", key=f"learn_{row['listing_id']}", on_click=select_program, args=(row['listing_id'],))
        st.divider()

    cols = st.columns([1,1,1])
    with cols[0]:
        if st.session_state.page_number > 0:
            st.button("◀ Previous", on_click=go_prev)
    with cols[1]:
        st.markdown(f"**Page {st.session_state.page_number+1}/{total_pages}**")
    with cols[2]:
        if st.session_state.page_number < total_pages-1:
            st.button("Next ▶", on_click=go_next)

else:
    # --- Detail View ---
    prog = df[df['listing_id'] == st.session_state.selected_program].iloc[0]
    st.button("◀ Back", on_click=clear_selection)
    st.header(prog['program_name'])
    url = f"https://my.americorps.gov/mp/listing/viewListing.do?fromSearch=true&id={prog['listing_id']}"
    st.markdown(f"<a href='{url}' target='_blank' class='apply-btn'>Apply Now</a>", unsafe_allow_html=True)

    # Summary Card
    state = prog['program_state'].title()
    metro = str(prog['metro_area']).strip("[]'") if pd.notna(prog['metro_area']) else ""
    location = f"{state}, {metro}" if metro else state
    st.markdown(f"""
    <div class='summary-card'>
      <h4>Program Summary</h4>
      <p><strong>Location:</strong> {location}</p>
      <p><strong>Dates:</strong> {format_date(prog['accept_start'])} – {format_date(prog['accept_end'])}</p>
      <p><strong>Schedule:</strong> {prog['work_schedule']}</p>
      <p><strong>Education:</strong> {prog['education_level']}</p>
      <p><strong>Age:</strong> {int(prog['age_minimum']) if pd.notna(prog['age_minimum']) else 'None'}+</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["Overview","Duties","Benefits","Terms","Skills","Areas","Contact"])
    with tabs[0]: st.write(prog['description'])
    with tabs[1]: st.write(prog['member_duties'])
    with tabs[2]: st.write(prog['program_benefits'])
    with tabs[3]: st.write(prog['terms'] if pd.notna(prog['terms']) else "None")
    with tabs[4]:
        for s in prog['skills'].split(','):
            s = s.strip()
            if s: st.markdown(f"<span class='pill-skill'>{s}</span>", unsafe_allow_html=True)
    with tabs[5]:
        for a in prog['service_areas'].split(','):
            a = a.strip()
            if a: st.markdown(f"<span class='pill'>{a}</span>", unsafe_allow_html=True)
    with tabs[6]: st.text(prog['contact'])
