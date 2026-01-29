import streamlit as st
from datetime import datetime, timedelta

# --- Cycle Predictor Logic ---
class CyclePredictor:
    def __init__(self, period_ranges):
        self.period_ranges = sorted(period_ranges, key=lambda x: x[0])
        self.period_start_dates = [start for start, _ in self.period_ranges]
        self.cycle_lengths = self._calculate_cycle_lengths()

    def _calculate_cycle_lengths(self):
        if len(self.period_start_dates) < 2:
            return []

        cycle_lengths = [
            (self.period_start_dates[i + 1] - self.period_start_dates[i]).days
            for i in range(len(self.period_start_dates) - 1)
        ]

        self.avg_cycle_length = sum(cycle_lengths) / len(cycle_lengths)
        self.min_cycle_length = min(cycle_lengths)
        self.max_cycle_length = max(cycle_lengths)
        self.is_regular = (self.max_cycle_length - self.min_cycle_length) <= 7  # ACOG guideline

        return cycle_lengths

    def predict_next_period(self):
        if len(self.period_start_dates) < 2:
            return {"error": "Log at least 2 periods to predict."}

        last_period_start = self.period_start_dates[-1]
        predicted_start = last_period_start + timedelta(days=round(self.avg_cycle_length))

        range_start = last_period_start + timedelta(days=self.min_cycle_length)
        range_end = last_period_start + timedelta(days=self.max_cycle_length)

        return {
            "predicted_start_date": predicted_start.strftime("%Y-%m-%d"),
            "range": [range_start.strftime("%Y-%m-%d"), range_end.strftime("%Y-%m-%d")],
            "confidence": "Higher" if self.is_regular else "Lower",
            "regularity": "Regular" if self.is_regular else "Irregular",
            "based_on": f"{len(self.cycle_lengths)} cycles",
            "average_cycle_length": round(self.avg_cycle_length),
            "shortest_cycle": self.min_cycle_length,
            "longest_cycle": self.max_cycle_length
        }

    def get_current_phase(self, current_date=None):
        if not self.period_start_dates:
            return "Insufficient data"

        current_date = datetime.today() if not current_date else datetime.strptime(current_date, "%Y-%m-%d")
        last_start = self.period_start_dates[-1]
        days_since_last_period = (current_date - last_start).days

        if days_since_last_period < 0:
            return "Invalid date: before last period"

        cycle_day = days_since_last_period + 1

        if cycle_day <= 5:
            phase = "Menstrual Phase"
        elif cycle_day <= 12:
            phase = "Follicular Phase"
        elif cycle_day <= 15:
            phase = "Ovulatory Phase"
        else:
            phase = "Luteal Phase"

        return f"Cycle Day {cycle_day} — {phase}"

    def get_ovulation_and_fertility_window(self):
        if len(self.period_start_dates) < 2:
            return {"error": "Log at least 2 periods to calculate ovulation."}

        last_period_start = self.period_start_dates[-1]
        ovulation_day = last_period_start + timedelta(days=round(self.avg_cycle_length) - 14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=1)

        return {
            "ovulation_day": ovulation_day.strftime("%Y-%m-%d"),
            "fertile_window": [
                fertile_start.strftime("%Y-%m-%d"),
                fertile_end.strftime("%Y-%m-%d")
            ]
        }

# --- Streamlit App ---
st.set_page_config(page_title="Cycle Tracker", layout="centered")
st.title("Menstrual Cycle Tracker — Research-Based")

num_periods = st.number_input("How many past periods would you like to log?", min_value=2, max_value=10, value=2, step=1)

period_ranges = []
for i in range(num_periods):
    with st.expander(f"Period #{i + 1}"):
        start_date = st.date_input(f"Start Date {i + 1}", key=f"start_{i}")
        end_date = st.date_input(f"End Date {i + 1}", key=f"end_{i}")

        if start_date and end_date and start_date <= end_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.min.time())
            period_ranges.append((start_dt, end_dt))

if st.button("Predict Cycle Insights"):
    if len(period_ranges) < 2:
        st.warning("Please log at least 2 periods.")
    else:
        predictor = CyclePredictor(period_ranges)
        prediction = predictor.predict_next_period()

        if "error" in prediction:
            st.error(prediction["error"])
        else:
            st.subheader("📅 Next Period Prediction")
            st.success(f"Predicted Start Date: {prediction['predicted_start_date']}")
            st.markdown(f"**Prediction Range:** {prediction['range'][0]} to {prediction['range'][1]}")
            st.caption(f"Confidence: {prediction['confidence']} — Based on {prediction['based_on']}")

            st.subheader("🔁 Cycle Stats")
            st.markdown(f"- Average Cycle Length: {prediction['average_cycle_length']} days")
            st.markdown(f"- Shortest Cycle: {prediction['shortest_cycle']} days")
            st.markdown(f"- Longest Cycle: {prediction['longest_cycle']} days")
            st.markdown(f"- Regularity: **{prediction['regularity']}**")

            st.subheader("📍 Current Cycle Phase")
            st.markdown(f"**{predictor.get_current_phase()}**")

            ovulation_data = predictor.get_ovulation_and_fertility_window()
            if "error" in ovulation_data:
                st.warning(ovulation_data["error"])
            else:
                st.subheader("🌿 Ovulation & Fertile Window")
                st.markdown(f"- Expected Ovulation: **{ovulation_data['ovulation_day']}**")
                st.markdown(f"- Fertile Window: **{ovulation_data['fertile_window'][0]}** to **{ovulation_data['fertile_window'][1]}**")
