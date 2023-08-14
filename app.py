import streamlit as st
from langchain.vectorstores.weaviate import Weaviate
import weaviate
import os
from dotenv import load_dotenv

from utils.inbox_utils import inbox_user_input, get_inbox_conversation_chain
from utils.htmlTemplate import css

repo_id = "tiiuae/falcon-40b"

def main():
    load_dotenv()
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACE_APIKEY")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_APIKEY")
    client = weaviate.Client("http://localhost:8080")
    vectorstore = Weaviate(client, "Mails", "mailBody")

    st.set_page_config(page_title="Inbox Search", page_icon=":mailbox_with_mail:", layout="wide")
    st.write(css, unsafe_allow_html=True)
    st.header("Data Seeker :mag_right:")

    platform = st.sidebar.selectbox(label="Select platform", options=["Inbox", "LinkedIn"])

    if platform == "Inbox":
        question = st.text_input("Search your inbox:")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        
        if "conversation" not in st.session_state:
            st.session_state.conversation = get_inbox_conversation_chain(vectorstore)

        if st.button("Search"):
            with st.spinner("Searching..."):
                if question:
                    inbox_user_input(question)

    elif platform == "LinkedIn":
        st.write("Coming soon...")

if __name__ == "__main__":
    main()