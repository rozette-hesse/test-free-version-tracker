import streamlit as st
import datetime
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Cycle Tracker", layout="centered")
st.title("🔬 Research-Based")
st.header("🩸 Add New Period")

# Initialize session state
if "periods" not in st.session_state:
    st.session_state.periods = []

# Period input
new_start = st.date_input("Start Date", key="start")
new_end = st.date_input("End Date", key="end")

if st.button("Add Period"):
    if new_start and new_end and new_start <= new_end:
        st.session_state.periods.append((new_start, new_end))
        st.success("Period added.")
    else:
        st.error("Please enter valid start and end dates.")

# Display logged periods
st.subheader("📊 All Logged Periods")
if not st.session_state.periods:
    st.info("No periods logged yet.")
else:
    sorted_periods = sorted(st.session_state.periods, key=lambda x: x[0])
    for i, (start, end) in enumerate(sorted_periods):
        st.write(f"**Period #{i+1}:** {start} to {end}")

    # Compute cycle lengths
    cycle_lengths = []
    for i in range(1, len(sorted_periods)):
        prev_start = sorted_periods[i-1][0]
        curr_start = sorted_periods[i][0]
        diff = (curr_start - prev_start).days
        cycle_lengths.append(diff)

    # Predict next cycle start
    st.subheader("🗓️ Next Period Prediction")
    if len(cycle_lengths) >= 3:
        # Use linear regression model
        X = np.arange(len(cycle_lengths)).reshape(-1, 1)
        y = np.array(cycle_lengths)
        model = LinearRegression()
        model.fit(X, y)
        next_cycle_length = int(model.predict(np.array([[len(cycle_lengths)]])).round())
        prediction_method = "ML model (Linear + Smoothing)"
    elif len(cycle_lengths) >= 2:
        next_cycle_length = int(np.median(cycle_lengths))
        prediction_method = "Median fallback"
    else:
        next_cycle_length = None

    if next_cycle_length:
        last_period_start = sorted_periods[-1][0]
        predicted_start = last_period_start + datetime.timedelta(days=next_cycle_length)
        prediction_range = (predicted_start - datetime.timedelta(days=3), predicted_start + datetime.timedelta(days=3))

        st.success(f"**Predicted Start Date:** {predicted_start}")
        st.write(f"**Prediction Range:** {prediction_range[0]} to {prediction_range[1]}")
        st.write(f"**Prediction Method:** {prediction_method}")

        # Ovulation and Fertile Window
        ovulation_date = predicted_start - datetime.timedelta(days=14)
        fertile_start = ovulation_date - datetime.timedelta(days=3)
        fertile_end = ovulation_date + datetime.timedelta(days=3)

        st.subheader("🌿 Ovulation & Fertile Window")
        st.write(f"**Expected Ovulation:** {ovulation_date}")
        st.write(f"**Fertile Window:** {fertile_start} to {fertile_end}")
    else:
        st.warning("Please log at least 2 periods to see predictions.")
