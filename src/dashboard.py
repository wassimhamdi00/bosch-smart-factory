"""Streamlit overview of synthetic machine readings and generated alarms."""

import streamlit as st

from src.monitor import database, generate, persist

st.set_page_config(page_title="Smart Factory Monitoring", layout="wide")
st.title("Smart Factory Monitoring")
st.caption("Offline demonstration using synthetic measurements; no live machinery connection.")

connection = database()
for sample in generate(n=100):
    persist(connection, sample)

summary = connection.execute(
    "SELECT machine_id, COUNT(*), ROUND(AVG(temperature), 1), "
    "ROUND(AVG(vibration), 1) FROM samples GROUP BY machine_id ORDER BY machine_id"
).fetchall()
st.subheader("Machine overview")
st.dataframe(
    [{
        "Machine": machine,
        "Readings": count,
        "Avg. temperature (°C)": temperature,
        "Avg. vibration (mm/s)": vibration,
    } for machine, count, temperature, vibration in summary],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Threshold alarms")
alarms = connection.execute(
    "SELECT machine_id, timestamp, kind, value FROM alarms ORDER BY timestamp"
).fetchall()
st.dataframe(
    [dict(machine_id=machine, timestamp=timestamp, alarm_type=kind, value=value)
     for machine, timestamp, kind, value in alarms],
    use_container_width=True,
    hide_index=True,
)
connection.close()
