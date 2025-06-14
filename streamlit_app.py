import streamlit as st
from orchestrator import handle_query
import os

if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Dubai Rental Assistant", layout="wide")
st.title("🏙️ Dubai Rental Assistant")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Paste a property link or ask anything about renting in Dubai."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing..."):
        response = handle_query(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
