import streamlit as st
import pandas as pd
import time
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
import random

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "tech.core.engine@gmail.com"
SENDER_PASSWORD = "nkpo liry nguz aogk"
RECIPIENT_EMAIL = "m.erfanzarabadipour@gmail.com"

NORMAL_HEART_RATE_MIN = 60
NORMAL_HEART_RATE_MAX = 100
LOW_OXYGEN_THRESHOLD = 90
EMAIL_INTERVAL = 300  
last_email_time = {"heart_rate": 0, "oxygen": 0}

REALTIME_URL = "https://script.google.com/macros/s/AKfycbwtHknz8x35Dg17AvxTiEsLGYzNmlihdEUwCRDKuE_TdwssDa-vGKzeNbVtifitagVI/exec"

def send_email(subject, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        st.success(f"Email sent: {subject}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

def check_alerts(heart_rate, oxygen_level):
    global last_email_time
    current_time = time.time()
    
    if heart_rate > NORMAL_HEART_RATE_MAX and current_time - last_email_time["heart_rate"] > EMAIL_INTERVAL:
        message = f"High Heart Rate Alert! Current heart rate: {heart_rate} bpm"
        send_email("High Heart Rate Alert", message)
        last_email_time["heart_rate"] = current_time

    elif heart_rate < NORMAL_HEART_RATE_MIN and current_time - last_email_time["heart_rate"] > EMAIL_INTERVAL:
        message = f"Low Heart Rate Alert! Current heart rate: {heart_rate} bpm"
        send_email("Low Heart Rate Alert", message)
        last_email_time["heart_rate"] = current_time

    if oxygen_level < LOW_OXYGEN_THRESHOLD and current_time - last_email_time["oxygen"] > EMAIL_INTERVAL:
        message = f"Low Oxygen Level Alert! Current oxygen level: {oxygen_level}%"
        send_email("Low Oxygen Level Alert", message)
        last_email_time["oxygen"] = current_time


def get_realtime_data():
    try:
        response = requests.get(REALTIME_URL)
        if response.status_code == 200:
            data = response.json()
            return data.get("heart_rate"), data.get("oxygen_level")
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
    return None, None


def generate_test_data():
    heart_rate = random.randint(50, 120)  
    oxygen_level = random.randint(85, 100)  
    return heart_rate, oxygen_level

st.title("📊 Real-Time Heart Rate and Oxygen Monitoring")
st.markdown("""
    Welcome to the Heart Rate and Oxygen Monitoring Dashboard!  
    Choose between **Real-Time Monitoring** or **Test Mode** to see how the system performs.  
    Alerts will be sent via email for abnormal conditions.  
""")

mode = st.selectbox("Select Monitoring Mode", ["Real-Time Mode", "Test Mode"])


if st.button("Start Monitoring"):
    st.success("Monitoring Started! Stop by refreshing the page.")
    placeholder_metrics = st.empty()
    if mode == "Test Mode":
        while True:
        
            heart_rate, oxygen_level = generate_test_data()

            with placeholder_metrics.container():
                st.metric("Heart Rate", f"{heart_rate} bpm")
                st.metric("Oxygen Level", f"{oxygen_level}%")

            check_alerts(heart_rate, oxygen_level)

            time.sleep(2)

    elif mode == "Real-Time Mode":
        placeholder_chart = st.empty()
        chart_data = pd.DataFrame(columns=["Heart Rate", "Oxygen Level"])
        fig, ax = plt.subplots()

        while True:

            heart_rate, oxygen_level = get_realtime_data()
            if heart_rate is None or oxygen_level is None:
                continue

            with placeholder_metrics.container():
                st.metric("Heart Rate", f"{heart_rate} bpm")
                st.metric("Oxygen Level", f"{oxygen_level}%")

            check_alerts(heart_rate, oxygen_level)

            chart_data = pd.concat([chart_data, pd.DataFrame({"Heart Rate": [heart_rate], "Oxygen Level": [oxygen_level]})])
            if len(chart_data) > 50:
                chart_data = chart_data.iloc[-50:]

            with placeholder_chart.container():
                ax.clear()
                ax.plot(chart_data["Heart Rate"], label="Heart Rate (bpm)", linestyle="-", marker="o")
                ax.plot(chart_data["Oxygen Level"], label="Oxygen Level (%)", linestyle="--", marker="x")
                ax.set_title("Live Monitoring")
                ax.set_xlabel("Time (updates)")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)

            time.sleep(2)
