import asyncio

import streamlit as st

import agent
from config import AWS_PROFILE, AWS_REGION

st.set_page_config(
    page_title="AWS Assistant",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ AWS Assistant")
st.caption("Inspect AWS resources and usage costs with AWS MCP.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("AWS connection")
    st.write(f"Profile: `{AWS_PROFILE}`")
    st.write(f"Default Region: `{AWS_REGION}`")

    st.caption(
        "The selected profile's IAM role controls AWS permissions."
    )

    if st.button("Check MCP tools"):
        try:
            with st.spinner("Connecting to AWS MCP..."):
                names = asyncio.run(agent.tool_names())

            st.success("AWS API tool discovered.")
            st.code("\n".join(names))

            st.caption(
                "Tool discovery does not verify resource permissions. "
                "Ask the assistant to check your AWS identity next."
            )

        except Exception as exc:
            st.error(str(exc))

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("Example questions")
    st.markdown(
        "- What AWS account and role are you using?\n"
        "- List my VPCs in us-east-1.\n"
        "- Show my deployed resources in us-east-1.\n"
        "- Show month-to-date usage charges by service."
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask about your AWS account")

if question:
    history = list(st.session_state.messages)

    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Checking AWS..."):
                answer, called = asyncio.run(
                    agent.ask(question, history)
                )

            st.markdown(answer)

            if called:
                with st.expander("Tools used"):
                    st.code("\n".join(called))

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            st.error(f"Request failed: {exc}")

            st.info(
                "Verify the role profile in your terminal:\n\n"
                f"aws sts get-caller-identity --profile {AWS_PROFILE}"
            )

            # Remove the unanswered question from saved history.
            st.session_state.messages.pop()