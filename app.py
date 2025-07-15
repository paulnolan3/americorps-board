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
  .similar-section {
    border-top: 2px solid #1550ed;
    margin-top: 36px;
    padding-top: 24px;
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
    st.session_state.selected_program = None
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

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
                  .replace("nan", "None")
        )
    df.fillna("None", inplace=True)
    df['accept_start'] = pd.to_datetime(df['accept_start'], format='%m/%d/%Y', errors='coerce')
    df['accept_end']   = pd.to_datetime(df['accept_end'],   format='%m/%d/%Y', errors='coerce')
    return df

# ... rest of code unchanged ...

    # === Similar Listings ===
    st.markdown("<div class='similar-section'><h3>You might also like...</h3>", unsafe_allow_html=True)

    def get_similarity_score(base, other):
        if base['work_schedule'] != other['work_schedule']:
            return 0
        base_areas = set(a.strip() for a in str(base['service_areas']).split(',') if a.strip())
        other_areas = set(a.strip() for a in str(other['service_areas']).split(',') if a.strip())
        base_skills = set(s.strip() for s in str(base['skills']).split(',') if s.strip())
        other_skills = set(s.strip() for s in str(other['skills']).split(',') if s.strip())
        shared_areas = len(base_areas & other_areas)
        shared_skills = len(base_skills & other_skills)
        return shared_areas * 3 + shared_skills * 1

    others = df[df['listing_id'] != prog['listing_id']].copy()
    others['similarity_score'] = others.apply(lambda row: get_similarity_score(prog, row), axis=1)
    top_similar = others[others['similarity_score'] > 0].sort_values(by='similarity_score', ascending=False).head(3)

    if top_similar.empty:
        st.write("No similar listings found.")
    else:
        for _, row in top_similar.iterrows():
            st.subheader(row['program_name'])
            st.write(f"**Location:** {row['program_state']}")
            st.write(f"**Schedule:** {row['work_schedule']}")
            st.write(f"**Similarity Score:** {row['similarity_score']}")
            st.button("View Listing", key=f"similar_{row['listing_id']}", on_click=select_program, args=(row['listing_id'],))
            st.divider()

    st.markdown("</div>", unsafe_allow_html=True)
