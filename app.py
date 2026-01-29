import streamlit as st
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Cycle Tracker", layout="centered")
st.title("🩸 Research-Based")
st.header("🚣 Add New Period")

if "periods" not in st.session_state:
    st.session_state.periods = []

with st.form(key="add_period"):
    start_date = st.date_input("Start Date", format="YYYY/MM/DD")
    end_date = st.date_input("End Date", format="YYYY/MM/DD")
    submitted = st.form_submit_button("Add Period")

    if submitted:
        if start_date <= end_date:
            st.session_state.periods.append((start_date, end_date))
            st.success("Period added.")
        else:
            st.error("End date must be after or equal to start date.")

st.divider()
st.subheader("🌟 All Logged Periods")

if st.session_state.periods:
    sorted_periods = sorted(list(set(st.session_state.periods)), key=lambda x: x[0])
    for i, (start, end) in enumerate(sorted_periods, 1):
        st.markdown(f"**Period #{i}:** {start} to {end}")
else:
    st.info("No periods logged yet.")
    sorted_periods = []

st.divider()

if len(sorted_periods) >= 2:
    # Calculate cycle lengths between consecutive periods
    cycle_lengths = [
        (sorted_periods[i + 1][0] - sorted_periods[i][0]).days
        for i in range(len(sorted_periods) - 1)
    ]
    unique_lengths = list(set(cycle_lengths))

    # ML prediction: Linear regression if variance > 0
    X = np.array(range(len(cycle_lengths))).reshape(-1, 1)
    y = np.array(cycle_lengths)
    model_type = ""

    if len(unique_lengths) > 1:
        model = LinearRegression()
        model.fit(X, y)
        next_cycle_length = int(model.predict(np.array([[len(cycle_lengths)]])).round())
        model_type = "ML model (Linear Regression)"
    else:
        next_cycle_length = cycle_lengths[-1]
        model_type = "Rule-based (last cycle)"

    predicted_start = sorted_periods[-1][0] + datetime.timedelta(days=next_cycle_length)
    prediction_range = (
        predicted_start - datetime.timedelta(days=3),
        predicted_start + datetime.timedelta(days=3)
    )

    st.subheader("📅 Next Period Prediction")
    st.success(f"Predicted Start Date: {predicted_start}")
    st.markdown(f"**Prediction Range:** {prediction_range[0]} to {prediction_range[1]}")
    st.markdown(f"**Confidence:** {'Higher' if len(unique_lengths) == 1 else 'Lower'} — Based on {len(cycle_lengths)} cycles")
    st.markdown(f"**Prediction Method:** {model_type}")
else:
    st.warning("Please log at least 2 valid periods to see predictions.")
