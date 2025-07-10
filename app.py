import streamlit as st
import pandas as pd

# Sample data: Replace this with actual data loading logic later
data = [
    {
        "Listing ID": "123584",
        "Program": "The Landing Place - Rockland, Maine",
        "Work Schedule": "Full Time",
        "Program Locations": "MAINE",
        "Member Duties": "Our AmeriCorps Fellow will create, facilitate, and evaluate a leadership program for TLP youth (ages 16-19) focusing on confidence, leadership, self-awareness, job readiness, community involvement, and civic understanding. Ideal candidates are team-driven, enthusiastic about youth and community engagement, and have an interest or understanding of strength-based approaches and authentic relationship building. The Fellow will incorporate trauma-informed care to counter adverse childhood experiences (ACEs) by increasing positive childhood experiences.",
        "Skills": "Youth Development, Social Services, Teaching/Tutoring, First Aid, Education, Communications, Team Work, Leadership, General Skills, Community Organization, Conflict Resolution",
        "Service Areas": "Public Health AmeriCorps, Housing, Children/Youth, Community Outreach, Education, Homelessness, Community and Economic Development",
        "Terms": "Permits working at another job during off hours, Car recommended, Permits attendance at school during off hours",
        "Program Benefits": "Living Allowance, Childcare assistance if eligible, Education award upon successful completion of service, Training, Health Coverage"
    },
    {
        "Listing ID": "123702",
        "Program": "WI Association and Runaway Services",
        "Work Schedule": "Full Time",
        "Program Locations": "WISCONSIN",
        "Member Duties": "Make direct contact with homeless or at risk youth providing them with prevention materials, referral information and offering them healthy alternatives to life on the streets such as food vouchers, transportation vouchers, referrals for physical and mental health services and a safe long term living arrangements. Provide on site advocacy to runaways and mediation for families work with law enforcement to provide them with information on runaway services to promote referrals to runaway programs. Lead youth groups with the goal of providing prevention materials in order to promote access to program services; AOAD counseling, resume preparation, mental and physical healthcare referrals as needed and short term shelter. Increase community knowledge of issues facing runaways through presentations with the goal of promoting referrals.",
        "Skills": "Counseling, Youth Development, Communications, Conflict Resolution, Community Outreach",
        "Service Areas": "Homelessness, Community Outreach, Housing, Education, Children/Youth",
        "Terms": "Uniforms provided and required",
        "Program Benefits": "Childcare assistance if eligible, Training, Health Coverage, Education award upon successful completion of service, Living Allowance"
    }
]

df = pd.DataFrame(data)

st.set_page_config(page_title="AmeriCorps Service Opportunities", layout="wide")
st.title("AmeriCorps Explorer")

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
    st.warning("No opportunities match your filters.")
else:
    for _, row in filtered_df.iterrows():
        with st.expander(row["Program"]):
            for field in row.index:
                if field != "Program":
                    st.markdown(f"**{field}:** {row[field]}")
