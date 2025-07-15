import streamlit as st
import pandas as pd
from datetime import date, timedelta

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
  }
  .pill-filter.selected {
    background-color: #112542;
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
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = set()

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

def select_program(pid):
    st.session_state.selected_program = pid

def clear_selection():
    st.session_state.selected_program = None

def toggle_tag(tag):
    if tag in st.session_state.selected_tags:
        st.session_state.selected_tags.remove(tag)
    else:
        st.session_state.selected_tags.add(tag)

def clear_all_filters():
    st.session_state.selected_tags = set()
    st.experimental_rerun()

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
selected_work = [opt for opt in ["Full Time", "Part Time", "Summer"] if st.sidebar.checkbox(opt, value=True)]
apply_soon = st.sidebar.checkbox("Apply soon (Deadline in next 2 weeks)")

# === Main View ===
if st.session_state.selected_program is None:
    st.title("AmeriCorps Opportunities")
    
    search_query = st.text_input("🔍 Search opportunities")

    # === Tag Filters Below Search ===
    st.markdown("**Filter by Service Area**")
    tag_options = ["Education", "Disaster Relief", "Environment", "Health", "Veterans"]
    tag_html = ""
    for tag in tag_options:
        selected = 'selected' if tag in st.session_state.selected_tags else ''
        tag_html += f'<span class="pill-filter {selected}" onClick="window.location.href='#{tag}'">{tag}</span>'
    st.markdown(tag_html, unsafe_allow_html=True)
    for tag in tag_options:
        if st.button(tag, key=f"tag_{tag}"):
            toggle_tag(tag)

    # === Filter Listings ===
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
    if search_query:
        query = search_query.lower()
        filtered = filtered[filtered.apply(lambda row: any(query in str(row[fld]).lower() for fld in [
            'program_name','description','member_duties','program_benefits','skills','service_areas'
        ]), axis=1)]
    if st.session_state.selected_tags:
        filtered = filtered[filtered['service_areas'].apply(lambda sa: any(tag in sa for tag in st.session_state.selected_tags))]

    # === Count + Clear Button ===
    st.markdown(f"**Showing {len(filtered)} results**")
    st.button("Clear All Filters", on_click=clear_all_filters)

    # === Display Listings ===
    for _, row in filtered.iterrows():
        st.subheader(row['program_name'])
        st.write(f"State: {row['program_state'].title()}")
        start = format_date(row['accept_start'])
        end = format_date(row['accept_end'])
        st.write(f"Accepting Applications: {start} → {end}")
        st.button("Learn more", key=f"learn_{row['listing_id']}", on_click=select_program, args=(row['listing_id'],))
        st.divider()

# === Detail View ===
else:
    prog = df.loc[df['listing_id'] == st.session_state.selected_program].iloc[0]
    st.button("◀ Back to search", on_click=clear_selection)

    col1, col2 = st.columns(2)
    with col1:
        st.header(prog['program_name'])
        url = f"https://my.americorps.gov/mp/listing/viewListing.do?fromSearch=true&id={prog['listing_id']}"
        st.markdown(f'<a href="{url}" target="_blank" class="apply-btn">Apply Now</a>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with col2:
        location = f"{prog['program_state'].title()}, {prog['metro_area'].strip('[]\' ')}" if prog['metro_area'] else prog['program_state'].title()
        start = format_date(prog['accept_start'])
        end = format_date(prog['accept_end'])
        age = f"{prog['age_minimum']}+" if prog['age_minimum'] else "None"
        st.markdown(f"""
        <div class="summary-card">
          <h4 style="margin:0 0 8px;">Program Summary</h4>
          <p><strong>🗺 Location:</strong> {location}</p>
          <p><strong>📅 Dates:</strong> {start} – {end}</p>
          <p><strong>💼 Schedule:</strong> {prog['work_schedule']}</p>
          <p><strong>🎓 Education:</strong> {prog['education_level']}</p>
          <p><strong>✅ Age:</strong> {age}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    tabs = st.tabs(["💬 Overview", "🛠 Duties", "💵 Benefits", "☑️ Terms", "📚 Skills", "🌐 Service Areas", "✉️ Contact"])
    with tabs[0]:
        st.write(prog.get('description', ''))
        st.write(f"**Listing ID:** {prog['listing_id']}")
    with tabs[1]:
        st.write(prog['member_duties'])
    with tabs[2]:
        st.write(prog['program_benefits'])
    with tabs[3]:
        terms_text = prog['terms'] if pd.notna(prog['terms']) else "None"
        st.write(terms_text)
    with tabs[4]:
        skills = [s.strip() for s in prog['skills'].split(',') if s.strip()]
        st.markdown("".join(f'<span class="pill-skill">{s}</span>' for s in skills), unsafe_allow_html=True)
    with tabs[5]:
        areas = [a.strip() for a in prog['service_areas'].split(',') if a.strip()]
        st.markdown("".join(f'<span class="pill">{a}</span>' for a in areas), unsafe_allow_html=True)
    with tabs[6]:
        st.text(prog['contact'])
