import streamlit as st
import datetime
import numpy as np
from statistics import median
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Cycle Tracker", layout="centered")

st.title("🌟 Research-Based")
st.header("🛳️ Add New Period")

# Input form
with st.form("period_form"):
    new_start = st.date_input("Start Date", key="start")
    new_end = st.date_input("End Date", key="end")
    submitted = st.form_submit_button("Add Period")

    if submitted:
        if new_start and new_end and new_start <= new_end:
            if "periods" not in st.session_state:
                st.session_state.periods = []
            st.session_state.periods.append((new_start, new_end))
            st.success("Period added.")
        else:
            st.error("Invalid dates. Start must be before end.")

# Retrieve periods
periods = st.session_state.get("periods", [])
sorted_periods = sorted(list(set(periods)))

st.markdown("---")
st.header("📊 All Logged Periods")
if not sorted_periods:
    st.info("No periods logged yet.")
else:
    for i, (start, end) in enumerate(sorted_periods):
        st.write(f"**Period #{i+1}:** {start} to {end}")

# --- ML prediction logic ---
if len(sorted_periods) >= 2:
    cycle_lengths = [
        (sorted_periods[i + 1][0] - sorted_periods[i][0]).days
        for i in range(len(sorted_periods) - 1)
    ]

    # Remove invalid or duplicate cycles (e.g., <15 days)
    cycle_lengths = [cl for cl in cycle_lengths if cl >= 15]

    if len(cycle_lengths) < 2:
        st.warning("Not enough valid cycle data for prediction.")
    else:
        if len(cycle_lengths) < 3:
            predicted_cycle_length = int(median(cycle_lengths))
            prediction_method = "Median fallback"
        else:
            X = np.arange(len(cycle_lengths)).reshape(-1, 1)
            y = np.array(cycle_lengths)
            model = LinearRegression().fit(X, y)
            next_index = np.array([[len(cycle_lengths)]])
            lr_pred = model.predict(next_index)[0]
            exp_smooth = np.mean(cycle_lengths[-3:])
            predicted_cycle_length = int(round((lr_pred + exp_smooth) / 2))
            prediction_method = "ML model (Linear + Smoothing)"

        last_start = sorted_periods[-1][0]
        predicted_start = last_start + datetime.timedelta(days=predicted_cycle_length)
        prediction_range = (
            predicted_start - datetime.timedelta(days=3),
            predicted_start + datetime.timedelta(days=3),
        )

        st.markdown("---")
        st.header("📅 Next Period Prediction")
        st.success(f"**Predicted Start Date:** {predicted_start}")
        st.write(f"**Prediction Range:** {prediction_range[0]} to {prediction_range[1]}")
        st.caption(f"Confidence: {'Lower' if len(cycle_lengths) < 4 else 'Higher'} — Based on {len(cycle_lengths)} cycles")
        st.caption(f"Prediction Method: {prediction_method}")
