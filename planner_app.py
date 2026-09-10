import sys
try:
    import pysqlite3 as sqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass


import streamlit as st
from datetime import date
from travel_agent_task import guide_expert, location_expert, planner_expert
from travel_agent_task import location_task, guide_task, planner_task
from travel_plan_utils import retrieve_relevant_docs_fn
from crewai import Crew, Process


# ------------------------ Streamlit Page Config ------------------------
st.set_page_config(page_title="AI Trip Planner", page_icon="🌍", layout="centered")

# ------------------------ Dark Theme Styling ------------------------
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #ffffff;
    }
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stDateInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div > div {
        color: white;
        background-color: #1e1e1e;
    }
    .stButton > button {
        background-color: #333333;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #555555;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Header ------------------------
st.title("🌍 Smart Travel Planner")
st.subheader("Plan your trip effortlessly with multi-agent AI + RAG")

# ------------------------ Input Form ------------------------
with st.form("travel_form"):
    from_city = st.text_input("✈️ From City", placeholder="e.g., New York")
    destination_city = st.text_input("📍 Destination City", placeholder="e.g., Paris")
    interests = st.text_input("🎯 Your Interests (e.g., sightseeing, food, adventure)", placeholder="e.g., sightseeing, food")

    raw_date_from = st.date_input("📅 Departure Date", date.today())
    raw_date_to = st.date_input("📅 Return Date", date.today())

    date_from = raw_date_from.strftime("%m-%d-%Y")
    date_to = raw_date_to.strftime("%m-%d-%Y")

    budget = st.text_input("💰 Budget", placeholder="e.g., $2000")

    submit = st.form_submit_button("🧠 Generate Travel Plan")

# ------------------------ Crew Execution ------------------------
if submit:
    st.info("Planning your trip... ✈️")

    doc_context = retrieve_relevant_docs_fn(destination_city)

    # Planner task (can include doc_context if integrated)
    loc_task = location_task(doc_context, location_expert, from_city, destination_city, date_from, date_to, budget)
    guid_task = guide_task(doc_context, guide_expert, destination_city, interests, date_from, date_to, budget)
    plan_task = planner_task([loc_task, guid_task], planner_expert, destination_city, interests, date_from, date_to, budget)

    crew = Crew(
        agents=[location_expert, guide_expert, planner_expert],
        tasks=[loc_task, guid_task, plan_task],
        process=Process.sequential,
        full_output=True,
        share_crew=False,
        verbose=True
    )

    result = crew.kickoff()
    st.success("✅ Travel Plan Generated!")

    # Output
    st.markdown("### 🗺️ Final Travel Plan:")
    st.markdown(result)

    # Optional: Save plan to a .md file
    st.download_button(
    label="🧠 Download Plan",
    data=str(result),  # convert CrewOutput to plain text
    file_name=f"{destination_city}_travel_plan.txt",
    mime="text/plain"
)