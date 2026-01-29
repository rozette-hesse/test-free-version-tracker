import streamlit as st
from datetime import datetime, timedelta
from statistics import median
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Cycle Tracker", layout="centered")

st.title("🩺 Research-Based")
st.header("🩷 Add New Period")

if "periods" not in st.session_state:
    st.session_state["periods"] = []

with st.form("period_form"):
    new_start = st.date_input("Start Date")
    new_end = st.date_input("End Date")
    submitted = st.form_submit_button("Add Period")

    if submitted:
        if new_start and new_end and new_start <= new_end:
            new_period = (new_start, new_end)
            if new_period not in st.session_state.periods:
                st.session_state.periods.append(new_period)
                st.success("Period added.")
                st.rerun()
            else:
                st.warning("This period is already logged.")
        else:
            st.error("Please ensure the dates are valid.")

st.subheader("📊 All Logged Periods")
if st.session_state.periods:
    sorted_periods = sorted(st.session_state.periods, key=lambda x: x[0])
    for i, (start, end) in enumerate(sorted_periods):
        st.markdown(f"**Period #{i+1}:** {start} to {end}")
else:
    st.info("No periods logged yet.")

if len(sorted_periods) < 2:
    st.warning("Please log at least 2 periods to see predictions.")
    st.stop()

# --- Calculate cycle lengths ---
cycle_start_dates = sorted([start for start, end in sorted_periods])
raw_cycle_lengths = [
    (cycle_start_dates[i + 1] - cycle_start_dates[i]).days
    for i in range(len(cycle_start_dates) - 1)
]

# --- Filter invalid cycles (shorter than 15 days or longer than 90) ---
cycle_lengths = [cl for cl in raw_cycle_lengths if 15 <= cl <= 90]

if len(cycle_lengths) < 1:
    st.warning("Not enough valid cycle data to predict.")
    st.stop()

# --- Predict next cycle start ---
last_period_start = cycle_start_dates[-1]

if len(cycle_lengths) < 3:
    # Use median
    predicted_cycle_length = median(cycle_lengths)
    prediction_method = "Median (fallback)"
else:
    # Linear Regression + Exponential Smoothing
    x = np.arange(len(cycle_lengths)).reshape(-1, 1)
    y = np.array(cycle_lengths)
    model = LinearRegression().fit(x, y)
    lr_pred = model.predict(np.array([[len(cycle_lengths)]]))[0]
    exp_smooth = np.mean(cycle_lengths[-3:])
    predicted_cycle_length = (lr_pred + exp_smooth) / 2
    prediction_method = "ML model (Linear + Smoothing)"

predicted_start_date = last_period_start + timedelta(days=round(predicted_cycle_length))
prediction_range = (
    last_period_start + timedelta(days=round(predicted_cycle_length - 5)),
    last_period_start + timedelta(days=round(predicted_cycle_length + 5))
)

st.subheader("🗓️ Next Period Prediction")
st.success(f"Predicted Start Date: {predicted_start_date}")
st.write(f"**Prediction Range:** {prediction_range[0]} to {prediction_range[1]}")
st.caption(f"Confidence: {'Higher' if len(cycle_lengths) >= 3 else 'Lower'} — Based on {len(cycle_lengths)} cycles")
st.caption(f"Prediction Method: {prediction_method}")
