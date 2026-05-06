import streamlit as st
from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
import time

st.set_page_config(page_title="RLA Insurance", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def load_llm():
    return Ollama(model="llama3:latest")

try:
    llm = load_llm()
except Exception as e:
    st.error(f"LLM error: {e}")

state_defaults = {
    "stage": "login",
    "ref_number": "11111111",   # fixed mismatch
    "claim_number": "123456",
    "uploaded_docs": {},
    "dan_chat": [],
    "bell_chat_history": []
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# initialize bell memory (fixed assignment)
if "bell_memory" not in st.session_state:
    st.session_state.bell_memory = ConversationBufferMemory()

## agent setup

bell_template = """You are 'Bell', an empathetic and highly professional AI assistant for RLA Insurance.
Your current task is to help the customer Mr. Smith lodge a new Income Protection Claim.
Follow these steps naturally in your conversation:
1. Greet the customer and express empathy if they mention an injury or illness.
2. Ask for their Policy Number.
3. Once they provide the Policy Number, ask them for the specific reason for their claim (e.g., Temporary disability, trauma etc).
4. Once they provide the reason, inform them that you will email the required claim forms and a document checklist.
5. Tell them their Query Reference number is '11111111' and instruct them to click the 'Proceed to Document Upload' button below the chat when they are ready.

Keep your responses concise, conversational, and user-friendly. Do not break character. Do not make up a policy number for them.

Current Conversation:
{history}
Customer: {input}
Bell:"""

bell_prompt = PromptTemplate(input_variables=["history", "input"], template=bell_template)

bell_chain = ConversationChain(
    llm=llm,
    memory=st.session_state.bell_memory,
    prompt=bell_prompt
)

# ClaimsXpert

def claims_xpert_analyze(text_content):
    xpert_prompt = PromptTemplate.from_template(
        """You are 'ClaimsXpert', an AI assistant for RLA Insurance Case Managers.
Review the following extracted text from a customer's claim document.
Summarize the nature of the injury/illness, recommended rest period, and state if it is clear to proceed.

Document Text: {text}
Summary for Case Manager:"""
    )

    chain = xpert_prompt | llm
    return chain.invoke({"text": text_content})


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = "".join([page.extract_text() or "" for page in reader.pages])  # fixed None issue
        return text
    except:
        return "SOME random text from docsss"


def navigate_to(stage):
    st.session_state.stage = stage
    st.rerun()


## UI

st.title("RLA Insurance")

# stage 1 login
if st.session_state.stage == "login":
    st.subheader("Login to RLA App")
    with st.container(border=True):
        st.write("MFA 1 enter otp sent to mobile")
        otp_mobile = st.text_input("Mobile OTP: ", type="password")

        if otp_mobile:
            st.success("Authentication success")
            st.write("MFA 2 enter otp sent to email")
            otp_email = st.text_input("Email OTP: ", type="password")

            if otp_email:
                st.success("Authentication Successful")
                if st.button("Click OK to Proceed"):
                    navigate_to("home")

# stage 2 home
elif st.session_state.stage == "home":
    st.subheader("Welcome back Mr Smith")
    with st.chat_message("assistant"):
        st.write("**Bell:** Hi, Mr Smith, Can I help you with any query")

    col1, col2, col3 = st.columns(3)
    if col1.button("Lodge a new claim"):
        navigate_to("intake")
    if col2.button("Resume Existing Query"):
        navigate_to("resume")   # fixed case
    if col3.button("Check Claim Status"):
        navigate_to("status")

    st.divider()

    if st.button("Back Office: Case Manager Portal"):
        navigate_to("assessment")

# stage 3 intake
elif st.session_state.stage == "intake":
    st.subheader("Chat with Bell")
    st.info("Bell will guide you through lodging your claim. Tell Bell about your injury to begin")

    for msg in st.session_state.bell_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("E.g., 'Hi bell, I fractured my leg and need to lodge a claim.'"):
        st.session_state.bell_chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Bell is typing"):
                response = bell_chain.predict(input=prompt)
                st.markdown(response)

        st.session_state.bell_chat_history.append({"role": "assistant", "content": response})

        st.divider()

        if st.button("Proceed to Document Upload"):
            st.info("*Simulated: Email sent to Mr. Smith with blank forms.*")
            time.sleep(2)
            navigate_to("resume")

# stage 4 resume
elif st.session_state.stage == "resume":
    st.subheader("Resume Claim Upload")
    st.write("Please enter your reference number to upload docs")

    ref_input = st.text_input("Query Reference Number")

    if ref_input == st.session_state.ref_number:
        st.success("History Retrieved. Please upload the required Docs")
        st.write("### Required Documents")

        doc1 = st.file_uploader("Medical Evidence", type=["pdf"])

        if doc1:
            st.session_state.uploaded_docs = {"medical": doc1}  # fixed key

            with st.spinner("AI Bell is validating document types...."):
                time.sleep(2)

            st.success("Validation Complete")
            st.write(f"Thank you. Your case has been moved to the assessment queue. You may track the status using claim number **{st.session_state.claim_number}**.")

            if st.button("Return to Home"):
                navigate_to("home")

# stage 6 assessment
elif st.session_state.stage == "assessment":
    st.subheader("Back Office Case Manager Portal")
    st.write("**Logged in as:** Case Manager Dan")

    with st.expander("View case files: Mr Smith"):
        if st.session_state.uploaded_docs:
            st.write("Medical Evidence Received")
        else:
            st.write("Docs missing")

    st.divider()
    st.markdown("### Chat with ClaimsXpert")

    for msg in st.session_state.dan_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Message ClaimsXpert"):
        st.session_state.dan_chat.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("ClaimsXpert is reviewing the files...."):
                if "medical" in st.session_state.uploaded_docs:
                    doc_text = extract_text_from_pdf(st.session_state.uploaded_docs["medical"])
                else:
                    doc_text = "Some random Textsss....."

                response = claims_xpert_analyze(doc_text)

                formatted_response = f"""**ClaimsXpert:** Hi Dan. All required documents have been received.

**Analysis:** {response}

You may proceed with the claim payment."""

                st.markdown(formatted_response)

                st.session_state.dan_chat.append({"role": "assistant", "content": formatted_response})

        st.divider()

        if st.button("Return to Customer App(Home)"):
            navigate_to("home")