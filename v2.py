import streamlit as st
import random
from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from fake_db import load_fake_db

st.set_page_config(page_title="RLA Insurance", layout="wide")

#LLM
@st.cache_resource
def load_llm():
    return Ollama(model="llama3:latest")

llm = load_llm()

#Loading fake db
if "db" not in st.session_state:
    st.session_state.db = load_fake_db()

#Session State
if "stage" not in st.session_state:
    st.session_state.stage = "login"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "current_policy" not in st.session_state:
    st.session_state.current_policy = None

role = st.sidebar.selectbox("Login as", ["Customer", "Case Manager (Dan)"])

# bell Prompt
def get_bell_prompt(status):
    return PromptTemplate(
        input_variables=["history", "input"],
        template=f"""
You are 'Bell', an AI assistant for RLA Insurance.

Customer Claim Status: {status}

Rules:
- If Approved → inform politely and next steps
- If Rejected → explain politely and suggest retry
- If Pending → ask user to wait
- If No Claim → guide to create claim

Keep responses short and helpful.

Conversation:
{{history}}
Human: {{input}}
Bell:"""
    )

# PyPDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

# ClaimXpert prompt
def claims_xpert_analyze(text_content):
    prompt = PromptTemplate.from_template(
        """Summarize:
- Injury/illness
- Rest period
- Missing info

Text:
{text}

Summary:"""
    )
    chain = prompt | llm
    return chain.invoke({"text": text_content})

# UI Flow
if role == "Customer":

    st.title("RLA Insurance - Customer Portal")

    # Login
    if st.session_state.stage == "login":
        st.subheader("Login")

        policy = st.text_input("Enter Policy Number")

        if st.button("Login"):
            if policy in st.session_state.db:
                st.session_state.current_policy = policy
                st.session_state.stage = "chat"
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid Policy Number")

    # Chat
    elif st.session_state.stage == "chat":

        policy = st.session_state.current_policy
        user_data = st.session_state.db[policy]
        status = user_data["status"]

        st.subheader(f"Welcome {user_data['name']}")

        # Show status
        st.info(f"Claim Status: {status}")

        # Chat setup
        bell_chain = ConversationChain(
            llm=llm,
            memory=st.session_state.memory,
            prompt=get_bell_prompt(status)
        )

        # Chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask something..."):

            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                response = bell_chain.predict(input=prompt)
                st.markdown(response)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

        st.divider()

        if status == "No Claim":
            if st.button("Start Claim"):
                st.session_state.stage = "upload"
                st.rerun()

    # Docuument Upload
    elif st.session_state.stage == "upload":

        st.subheader("Upload Documents")

        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file:
            st.success("File uploaded")

        if st.button("Submit Claim"):
            if uploaded_file:

                policy = st.session_state.current_policy
                claim_id = f"CLM{random.randint(1000,9999)}"

                st.session_state.db[policy]["status"] = "Pending"
                st.session_state.db[policy]["claim_id"] = claim_id
                st.session_state.db[policy]["documents"] = uploaded_file

                st.success(f"Claim Submitted! ID: {claim_id}")

                st.session_state.stage = "assessment"
                st.rerun()
            else:
                st.error("Upload document first")
                
    elif st.session_state.stage == "assessment":

        st.subheader("Processing Claim...")

        policy = st.session_state.current_policy
        data = st.session_state.db[policy]

        if data["analysis"] is None:

            file = data["documents"]

            with st.spinner("Analyzing document..."):
                text = extract_text_from_pdf(file)
                analysis = claims_xpert_analyze(text)

            st.session_state.db[policy]["analysis"] = analysis
            st.success("Submitted to Case Manager")

        else:
            st.info("Analysis already completed")

        st.write("### AI Summary")
        st.write(st.session_state.db[policy]["analysis"])

        if st.button("Back to Chat"):
            st.session_state.stage = "chat"
            st.rerun()
# DAN DASHBOARD 
elif role == "Case Manager (Dan)":

    st.title("Case Manager Dashboard")

    db = st.session_state.db

    for policy, data in db.items():

        st.subheader(f"{data['name']} ({policy})")

        st.write(f"Status: {data['status']}")
        st.write(f"Claim ID: {data.get('claim_id')}")

        if data["analysis"]:
            with st.expander("View Analysis"):
                st.write(data["analysis"])

        if data["status"] == "Pending":

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Approve {policy}"):
                    db[policy]["status"] = "Approved"
                    st.success("Approved")
                    st.rerun()

            with col2:
                if st.button(f"Reject {policy}"):
                    db[policy]["status"] = "Rejected"
                    st.error("Rejected")
                    st.rerun()

        st.divider()
