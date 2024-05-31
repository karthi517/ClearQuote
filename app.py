import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Load data

DATA_URL = "data.csv"


st.set_page_config(layout="wide")

# Function to load data
@st.cache_data(persist=True)
def load_data(DATA_URL):
    data = pd.read_csv(DATA_URL)
    return data

# Function to apply custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load data
df = load_data(DATA_URL)
original_data = df.copy()

# Embed custom CSS
local_css("styles.css")

if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(df)

st.title("AutoMobile🚗 Inspection🧐 Dashboard")
st.header("Checking is there any missing information from the data")

if st.checkbox("Show the count of missing values in the Data", False):
    st.subheader("Raw Data")
    st.write(df.isna().sum())


    missing_values = df.isna().sum()

    # Create a histogram using Plotly Express
    fig = px.histogram(missing_values, x=missing_values.index, y=missing_values.values, 
                    labels={'x': 'Columns', 'y': 'Number of Missing Values'}, 
                    title='Histogram of Missing Values per Column')

    # Streamlit app
    st.title('Missing Values Histogram')
    st.plotly_chart(fig)

st.title("Number of Vehicles Inspected by Date")
st.header("1.a.How many vehicles were inspected by date?")

Vehicles_inspected_count=df.groupby("Inspection date")["Vehicle ID"].nunique().reset_index()
Vehicles_inspected_count.columns = ["Inspection date", "Number of unique vehicles"]



# Display the bar chart using Plotly Express
fig = px.bar(Vehicles_inspected_count, x="Inspection date", y="Number of unique vehicles", 
             title="Number of Vehicles Inspected by Date", labels={"Vehicle ID": "Count"})

st.plotly_chart(fig)


parts_detected=df["Part detected"].value_counts().reset_index()
parts_detected.columns=["Part detected","Count"]

st.title("Frequency of Part Detected")

# Display the bar chart using Plotly Express
fig = px.bar(parts_detected, x="Part detected", y="Count", 
             title="Most Frequnetly detected Parts", labels={"Count": "Frequncy"})

st.plotly_chart(fig)

if st.checkbox("1.b.Which parts were most frequently detected?",False):
    st.write(parts_detected.iloc[0])

if st.checkbox("1.c.Which parts were least frequently detected?",False):
    st.write(parts_detected.iloc[-1])

# Streamlit app
st.title("Vehicle Inspection Coverage")

st.header("1.d.Which vehicles have been inspected thoroughly (max number of parts detected) and which ones have poor coverage?")

parts_inspected=df.groupby("Vehicle ID")["Part detected"].count().reset_index()

parts_inspected.columns=["Vehicle ID","Count of Part detected"]

max_parts_detected = parts_inspected["Count of Part detected"].max()
thorough_inspections = parts_inspected[parts_inspected["Count of Part detected"] == max_parts_detected]

# Identify vehicles with poor coverage (minimum parts detected)
min_parts_detected = parts_inspected["Count of Part detected"].min()
poor_coverage = parts_inspected[parts_inspected["Count of Part detected"] == min_parts_detected]



# Display thorough inspections
st.subheader("Thoroughly Inspected Vehicles")
st.write(thorough_inspections)

# Display vehicles with poor coverage
st.subheader("Vehicles with Poor Coverage")
st.write(poor_coverage)

# Display the bar chart using Plotly Express
fig = px.bar(parts_inspected, x="Vehicle ID", y="Count of Part detected", 
             title="Frequency of detected Parts by Vehicle ID", labels={"Count of Part detected": "Frequncy"})

st.plotly_chart(fig)


# Count the number of detections for each part in each inspection
part_counts = df.groupby(["Inspection ID", "Part detected"]).size().reset_index(name='Count')

# Classify parts based on coverage
part_counts['Coverage'] = part_counts['Count'].apply(lambda x: 'Good' if x >= 3 else 'Poor')

# Separate parts with good coverage and poor coverage
good_coverage = part_counts[part_counts['Coverage'] == 'Good']
poor_coverage = part_counts[part_counts['Coverage'] == 'Poor']

# Streamlit app
st.title("Coverage of Parts Detected in Inspections")
st.header("1.e.if a part is detected at least 3 times in an inspection, then it has good coverage. So which parts have poor coverage? And which parts have good coverage?")

# Display parts with good coverage
st.subheader("Parts with Good Coverage")
st.write(good_coverage)

# Display parts with poor coverage
st.subheader("Parts with Poor Coverage")
st.write(poor_coverage)

# Optionally, display a bar chart for context
fig = px.bar(part_counts, x="Part detected", y="Count", color="Coverage", 
             title="Coverage of Parts Detected", labels={"Count": "Number of Detections"})

st.plotly_chart(fig)


st.title("Vehicle Part Inspection Coverage")
st.header("1.f.if we select any one specific vehicle (Vehicle ID), then visually represent (e.g. in a heatmap),which parts have been detected/inspected well and which parts have not been detected well")

# Select a vehicle ID
vehicle_id = st.selectbox("Select a Vehicle ID", df["Vehicle ID"].unique())

# Filter data for the selected vehicle
vehicle_df = df[df["Vehicle ID"] == vehicle_id]

# Count the number of detections for each part in the selected vehicle
part_counts = vehicle_df.groupby(["Part detected"]).size().reset_index(name='Count')

# Classify parts based on coverage
part_counts['Coverage'] = part_counts['Count'].apply(lambda x: 'Good' if x >= 3 else 'Poor')

# Create a heatmap
fig = px.density_heatmap(part_counts, x="Part detected", y="Coverage", z="Count", color_continuous_scale="Viridis",
                         title=f"Heatmap of Part Detection Coverage for Vehicle ID: {vehicle_id}",
                         labels={"Count": "Number of Detections"})

# Display the heatmap
st.plotly_chart(fig)

# Display the part counts and coverage for reference
st.write(part_counts)

# Count the number of inspections for each vehicle
vehicle_inspection_counts = df["Vehicle ID"].value_counts().reset_index()
vehicle_inspection_counts.columns = ["Vehicle ID", "Inspection Count"]

# Identify the most and least inspected vehicles
most_inspected_vehicle = vehicle_inspection_counts.loc[vehicle_inspection_counts["Inspection Count"].idxmax()]
least_inspected_vehicle = vehicle_inspection_counts.loc[vehicle_inspection_counts["Inspection Count"].idxmin()]

# Streamlit app
st.title("Vehicle Inspection Frequency")
st.header("1.g.Which vehicles were inspected most number of times and which ones were inspected least number of times?")
# Display the most and least inspected vehicles
st.subheader("Most Inspected Vehicle")
st.write(most_inspected_vehicle)

st.subheader("Least Inspected Vehicle")
st.write(least_inspected_vehicle)

# Plot bar chart
fig = px.bar(vehicle_inspection_counts, x="Vehicle ID", y="Inspection Count",
             title="Vehicle Inspection Frequency",
             labels={"Vehicle ID": "Vehicle ID", "Inspection Count": "Number of Inspections"})

st.plotly_chart(fig)