import streamlit as st
from app.services.interactive_session import InteractiveSession
from markdown import markdown

# Setup the session
if 'session' not in st.session_state:
    st.session_state.session = InteractiveSession()
    st.session_state.session_id = st.session_state.session.start_session()
    st.session_state.history = []

st.title("💬 Campaign Optimization Assistant")

# Input area
user_input = st.text_input("Enter your message", "")

if st.button("Send") and user_input:
    if user_input.lower() == "exit":
        st.success("Session ended.")
        st.stop()

    if user_input.lower() == "history":
        history = st.session_state.session.get_session_history(st.session_state.session_id)
        st.subheader("📜 Conversation History")
        for msg in history:
            st.markdown(f"**{msg['type']}**:\n\n{msg['content']}", unsafe_allow_html=True)
    else:
        try:
            response = st.session_state.session.process_message(st.session_state.session_id, user_input)
            msg_type = response.get("type", "SYSTEM_RESPONSE")
            color = {
                'refinement': '🔧 Refined Response',
                'SYSTEM_RESPONSE': '💡 Response'
            }.get(msg_type, '💡 Response')

            st.subheader(color)
            st.markdown(response["content"], unsafe_allow_html=True)

            st.session_state.history.append({
                "input": user_input,
                "response": response["content"]
            })

            if response.get("is_done", False):
                st.success("✅ Session completed.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
