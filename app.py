import streamlit as st
from hindsight_client import Hindsight
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = "customer-support-agent"

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=API_KEY
)

st.set_page_config(
    page_title="Customer Support Memory Agent",
    page_icon="🤖"
)

st.title("🤖 Customer Support Memory Agent")
st.caption("AI support that remembers previous customer issues using Hindsight.")

customer_name = st.text_input(
    "Customer Name",
    placeholder="Enter your name"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("Describe your problem...")

if user_message:

    if not customer_name:
        st.warning("Please enter your name first.")
        st.stop()

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.write(user_message)

    try:

        # Save the customer's problem in Hindsight
        client.retain(
            bank_id=BANK_ID,
            content=f"""
            Customer: {customer_name}
            Customer support issue: {user_message}
            """
        )

        # Hindsight remembers previous information internally
        response = client.reflect(
            bank_id=BANK_ID,
            query=f"""
            You are a friendly customer support agent.

            Customer name: {customer_name}

            Current customer problem:
            {user_message}

            Use relevant information from this customer's previous
            support history stored in Hindsight.

            If this is a recurring problem, mention that you remember
            the previous issue.

            Give a short, practical and friendly answer.
            """
        )

        answer = response.text

        # Save the solution as memory
        client.retain(
            bank_id=BANK_ID,
            content=f"""
            Customer: {customer_name}
            Problem: {user_message}
            Support solution: {answer}
            """
        )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.success("🧠 Customer information saved to Hindsight memory.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")