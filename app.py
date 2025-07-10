import streamlit as st
import pandas as pd

# Sample data: Replace this with actual data loading logic later
data = [
    {
        "Listing ID": "123584",
        "Program": "The Landing Place - Rockland, Maine",
        "Work Schedule": "Full Time",
        "Program Locations": "MAINE",
        "Member Duties": "Create, facilitate, and evaluate a youth leadership program...",
        "Skills": "Youth Development, Social Services, Teaching/Tutoring",
        "Service Areas": "Public Health, Housing, Children/Youth",
        "Terms": "Permits working at another job during off hours, Car recommended",
        "Program Benefits": "Living Allowance, Childcare, Education award, Training, Health Coverage"
    },
    {
        "Listing ID": "123702",
        "Program": "WI Association and Runaway Services",
        "Work Schedule": "Full Time",
        "Program Locations": "WISCONSIN",
        "Member Duties": "Outreach to youth, referrals, education, and community presentations...",
        "Skills": "Counseling, Youth Development, Communications",
        "Service Areas": "Homelessness, Community Outreach, Housing",
        "Terms": "Uniforms provided and required",
        "Program Benefits": "Childcare, Training, Health Coverage, Education award, Living Allowance"
    }
]

df = pd.DataFrame(data)

st.set_page_config(page_title="AmeriCorps Job Board", layout="wide")
st.title("AmeriCorps Job Explorer")

# Sidebar Filters
with st.sidebar:
    st.header("Filter Results")
    states = st.multiselect("Location", options=df["Program Locations"].unique())
    schedules = st.multiselect("Work Schedule", options=df["Work Schedule"].unique())

# Apply filters
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["Program Locations"].isin(states)]
if schedules:
    filtered_df = filtered_df[filtered_df["Work Schedule"].isin(schedules)]

# Display results
if filtered_df.empty:
    st.warning("No jobs match your filters.")
else:
    for _, row in filtered_df.iterrows():
        with st.expander(row["Program"]):
            st.markdown(f"**Location:** {row['Program Locations']}")
            st.markdown(f"**Schedule:** {row['Work Schedule']}")
            st.markdown(f"**Member Duties:** {row['Member Duties']}")
            st.markdown(f"**Skills:** {row['Skills']}")
            st.markdown(f"**Service Areas:** {row['Service Areas']}")
            st.markdown(f"**Terms:** {row['Terms']}")
            st.markdown(f"**Benefits:** {row['Program Benefits']}")
