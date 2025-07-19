import streamlit as st
import pandas as pd
from datetime import date, timedelta
import streamlit.components.v1 as components  # for scroll-to-top JS

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

# === Session State ===
if 'selected_program' not in st.session_state:
    st.session_state.selected_program = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'show_tutorial' not in st.session_state:
    st.session_state.show_tutorial = True

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

# === Helpers ===
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
st.sidebar.markdown("---", help=None)
st.sidebar.markdown(
"""
<span style='color: gray; font-size: 0.85em;'>
Disclaimer: This tool is not a government website or endorsed by AmeriCorps. This tool helps with search and discovery. All applications must be submitted through the official <a href='https://my.americorps.gov/mp/listing/publicRequestSearch.do' target='_blank' style='color: gray;'>MyAmeriCorps portal</a>.
</span>
""", unsafe_allow_html=True)

# === Main View ===
if st.session_state.selected_program is None:
    # scroll top on main view using delayed scroll
    components.html(
        """
        <script>
          (function() {
            const scrollFn = () => {
              const ctx = window.top || window.parent || window;
              if (ctx) {
                ctx.scrollTo(0, 0);
                try { ctx.document.body.scrollTop = 0; ctx.document.documentElement.scrollTop = 0; } catch (e) {}
              }
            };
            setTimeout(scrollFn, 100);
          })();
        </script>
        """,
        height=1,
        width=1
    )

    st.title("AmeriCorps Explorer")
    # Filter and search logic...
    apply_filters = any([
        states,
        educations,
        len(selected_work) < 3,
        apply_soon,
        st.session_state.search_query.strip() != ""
    ])
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

    st.markdown(f"### There are <span class='pill'>{len(filtered)}</span> opportunities to serve.", unsafe_allow_html=True)
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
        filtered = filtered[filtered.apply(lambda r: any(q in str(r[f]).lower() for f in [
            'program_name','description','member_duties','program_benefits','skills','service_areas'
        ]), axis=1)]

    # Pagination
    total_pages = max(1, (len(filtered)-1)//RESULTS_PER_PAGE + 1)
    start = st.session_state.page_number * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    visible = filtered.iloc[start:end]

    for _, row in visible.iterrows():
        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        st.write(f"Accepting Applications: {format_date(row['accept_start'])} → {format_date(row['accept_end'])}")
        st.button("Learn more", key=f"learn_{row['listing_id']}", on_click=select_program, args=(row['listing_id'],))
        st.divider()

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.session_state.page_number > 0:
            st.button("◀ Previous", on_click=go_prev)
    with col2:
        st.markdown(f"**Page {st.session_state.page_number+1} of {total_pages}**")
    with col3:
        if st.session_state.page_number < total_pages-1:
            st.button("Next ▶", on_click=go_next)

# === Detail View ===
else:
    # scroll top on detail view
    components.html(
        """
        <script>
          (function() {
            const scrollFn = () => {
              const ctx = window.top || window.parent || window;
              if (ctx) {
                ctx.scrollTo(0, 0);
                try { ctx.document.body.scrollTop = 0; ctx.document.documentElement.scrollTop = 0; } catch (e) {}
              }
            };
            setTimeout(scrollFn, 100);
          })();
        </script>
        """,
        height=1,
        width=1
    )
    prog = df.loc[df['listing_id'] == st.session_state.selected_program].iloc[0]
    st.button("◀ Back to search", on_click=clear_selection)
    col1, col2 = st.columns([1,1])
    with col1:
        st.header(prog['program_name'])
        url = f"https://my.americorps.gov/mp/listing/viewListing.do?fromSearch=true&id={prog['listing_id']}"
        st.markdown(f'<a href="{url}" target="_blank" class="apply-btn">Apply Now</a>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with col2:
        state = prog['program_state'].title()
        metro = str(prog['metro_area']).strip("[]'") if pd.notna(prog['metro_area']) else ""
        location = f"{state}, {metro}" if metro else state
        st.markdown(f"""
        <div class="summary-card">
          <h4 style="margin:0 0 8px;">Program Summary</h4>
          <p><strong>🗽 Location:</strong> {location}</p>
          <p><strong>🗕 Dates:</strong> {format_date(prog['accept_start'])} – {format_date(prog['accept_end'])}</p>
          <p><strong>💼 Schedule:</strong> {prog['work_schedule']}</p>
          <p><strong>🎓 Education:</strong> {prog['education_level']}</p>
          <p><strong>✅ Age:</strong> {f"{int(prog['age_minimum'])}+" if pd.notna(prog['age_minimum']) else "None"}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    tabs = st.tabs(["💬 Overview","🛠 Duties","💵 Benefits","☑️ Terms","📚 Skills","🌐 Service Areas","✉️ Contact"])
    with tabs[0]:
        st.write(prog.get('description',''))
        st.write(f"**Listing ID:** {prog['listing_id']}")
    with tabs[1]:
        st.write(prog['member_duties'])
    with tabs[2]:
        st.write(prog['program_benefits'])
    with tabs[3]:
        st.write(prog['terms'] if pd.notna(prog['terms']) else "None")
    with tabs[4]:
        skills = [s.strip() for s in prog['skills'].split(',') if s.strip()]
        st.markdown("".join(f'<span class="pill-skill">{s}</span>' for s in skills), unsafe_allow_html=True)
    with tabs[5]:
        areas = [a.strip() for a in prog['service_areas'].split(',') if a.strip()]
        st.markdown("".join(f'<span class="pill">{a}</span>' for a in areas), unsafe_allow_html=True)
    with tabs[6]:
        st.text(prog['contact'])
