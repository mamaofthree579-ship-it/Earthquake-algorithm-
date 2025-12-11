import streamlit as st
from alerts.dispatcher import send_webhook
import json

st.title("Alerts & Humanitarian Overlay")

st.write("Dispatch a test alert to a webhook (demo). In production, alerts should go through verification & escalation.")

webhook_url = st.text_input("Webhook URL (for test)", "")
payload_text = st.text_area("Payload (JSON)", value=json.dumps({
    "source": "IHRAS-demo",
    "level": "ELEVATED",
    "message": "Test alert — please ignore",
}, indent=2), height=200)

if st.button("Send test webhook"):
    try:
        payload = json.loads(payload_text)
    except Exception as e:
        st.error(f"Payload is not valid JSON: {e}")
    else:
        ok, info = send_webhook(webhook_url, payload) if webhook_url else (False, "No webhook URL provided")
        if ok:
            st.success(f"Webhook sent — status {info}")
        else:
            st.error(f"Failed to send webhook: {info}")
