import streamlit as st
from langchain.vectorstores.weaviate import Weaviate
import weaviate
import os
from dotenv import load_dotenv
import openai

from llm_wrapper.wrapper import LLMWrapper
from utils.htmlTemplate import css
from utils.htmlTemplate import bot_template, user_template

repo_id = "tiiuae/falcon-40b"

def get_inbox_conversation(question, vectorstore):
    wrapper = LLMWrapper()
    wrapper.history = st.session_state.wrapper_history
    conversation = wrapper.generate_response(question, vectorstore, k=3)
    st.session_state.wrapper_history = True
    return conversation

def handel_user_input(user_query, conversation, vectrstore):

    st.session_state.chat_history.append(user_query)

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)

    res_box = st.empty()
    response_msg = []

    for r in conversation:
        if r["choices"][0]["delta"] == {}:
            break
        msg = r["choices"][0]["delta"]["content"]
        
        response_msg.append(msg)
        result = "".join(response_msg)
        res_box.markdown(bot_template.replace("{{MSG}}", result), unsafe_allow_html=True)

    st.session_state.chat_index += 1
    
    vectrstore.data_object.create({
        "conversation": str({"User": user_query,
                                "AI": result}), 
        "chatIndex": st.session_state.chat_index
        }, "Chat")

    st.session_state.chat_history.append(result)

def main():
    load_dotenv()
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACE_APIKEY")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_APIKEY")
    openai.api_key = os.getenv("OPENAI_APIKEY")

    vectorstore = weaviate.Client("http://localhost:8080",
            additional_headers={
                "X-HuggingFace-Api-Key": os.getenv("HUGGINGFACE_APIKEY")
    })
    st.set_page_config(page_title="Inbox Search", page_icon=":mailbox_with_mail:", layout="wide")
    st.write(css, unsafe_allow_html=True)
    st.header("Data Seeker :mag_right:")

    platform = st.sidebar.selectbox(label="Select platform", options=["Inbox", "LinkedIn"])

    if platform == "Inbox":
        question = st.text_input("Search your inbox:")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "wrapper_history" not in st.session_state:
            st.session_state.wrapper_history = False

        if "chat_index" not in st.session_state:
            st.session_state.chat_index = 0
        
        if st.button("Search"):
            with st.spinner("Searching..."):
                if question:
                    conversation = get_inbox_conversation(question, vectorstore)
                    handel_user_input(question, conversation, vectorstore)

    elif platform == "LinkedIn":
        st.write("Coming soon...")

if __name__ == "__main__":
    main()