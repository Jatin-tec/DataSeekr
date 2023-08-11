import streamlit as st
from langchain.vectorstores.weaviate import Weaviate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain import HuggingFaceHub
from langchain.prompts.chat import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
import weaviate
from utils.htmlTemplate import css, bot_template, user_template
import os
from dotenv import load_dotenv

repo_id = "tiiuae/falcon-40b"

def get_conversation_chain(vectorstore):
    momory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, verbose=True, input_key="question", output_key="answer")
    # llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={"temperature": 0.7, "max_length": 10000})
    llm = OpenAI(temperature=0.8, max_tokens=1000)

    system_template = """Use following pieces of context to answer the users question. 
    Following contexts are summarised texts from users inbox.
    ----------------
    {context}"""

    # Create the chat prompt templates
    messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}")
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    
    retriver = vectorstore.as_retriever(search_kwargs={"k": 10})

    conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriver, 
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": qa_prompt},
    max_tokens_limit=3000,
    memory=momory,
    verbose=True
    )
    print(f"Conversation chain created {conversation_chain}")
    return conversation_chain

def user_input(user_query):
    print(f"User query: {user_query}")
    response =  st.session_state.conversation({"question": user_query})
    print(f"Response: {response}")

    st.session_state.chat_history = response['chat_history']
    answer = response['answer']
    
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", answer), unsafe_allow_html=True)

def main():
    load_dotenv()
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACE_APIKEY")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_APIKEY")
    client = weaviate.Client("http://localhost:8080")
    vectorstore = Weaviate(client, "Mails", "mailBody")

    st.set_page_config(page_title="Inbox Search", page_icon=":mailbox_with_mail:", layout="wide")
    st.write(css, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = get_conversation_chain(vectorstore)

    st.header("Inbox Search :mailbox_with_mail:")

    question = st.text_input("Search your inbox:")

    if st.button("Search"):
        with st.spinner("Searching..."):
            if question:
                user_input(question)

    st.sidebar.selectbox(label="Select a mail", options=["Mail 1", "Mail 2", "Mail 3"])

if __name__ == "__main__":
    main()