import streamlit as st
import sys
from app.services.interactive_session import InteractiveSession  # Use your actual class

# --- Print capture setup ---
class StreamlitPrintCatcher:
    def __init__(self):
        if 'print_logs' not in st.session_state:
            st.session_state.print_logs = []
        self.logs = st.session_state.print_logs

    def write(self, message):
        if message.strip():
            self.logs.append(message)
            st.session_state.print_logs = self.logs

    def flush(self):
        pass

if 'print_logs' not in st.session_state:
    st.session_state.print_logs = []

if not hasattr(st.session_state, 'print_catcher_initialized') or not st.session_state.print_catcher_initialized:
    sys.stdout = StreamlitPrintCatcher()
    st.session_state.print_catcher_initialized = True
    print("Streamlit print catcher initialized.")

# --- Streamlit app setup ---
st.set_page_config(layout="wide", page_title="Campaign Optimization Assistant")

if 'session' not in st.session_state:
    st.session_state.session = InteractiveSession()
    st.session_state.session_id = st.session_state.session.start_session()
    st.session_state.chat_history = []
    print(f"New session started: {st.session_state.session_id}")
    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! How can I assist you with campaign optimization today?"})

st.title("💬 Campaign Optimization Assistant")

col_chat, col_logs = st.columns([3,1])

with col_chat:
    st.subheader("Conversation")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Enter your message", key="user_input_chat")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        print(f"User: {user_input}")

        if user_input.lower() == "exit":
            st.session_state.chat_history.append({"role": "assistant", "content": "Session ended. Goodbye!"})
            print("Session terminated by user.")
            st.stop()

        elif user_input.lower() == "history":
            full_history = st.session_state.session.get_session_history(st.session_state.session_id)
            history_display = "📜 **Conversation History**:\n\n"
            for msg in full_history:
                history_display += f"**{msg['type'].capitalize()}**: {msg['content']}\n\n"
            st.session_state.chat_history.append({"role": "assistant", "content": history_display})
            print("Displayed conversation history.")

        else:
            try:
                response = st.session_state.session.process_message(st.session_state.session_id, user_input)
                st.session_state.chat_history.append({"role": "assistant", "content": response["content"]})
                print(f"Bot: {response['content']}")

                if response.get("is_done", False):
                    st.success("✅ Session completed.")
                    print("Session marked as completed.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"❌ An error occurred: {str(e)}"})
                print(f"Error processing message: {e}")

        st.rerun()

with col_logs:
    st.subheader("🖨️ Print Logs")
    if st.session_state.print_logs:
        for log in reversed(st.session_state.print_logs):
            st.code(log, language='text')
    else:
        st.info("No logs yet.")
