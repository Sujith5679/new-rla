import streamlit as st
from langchain_community.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader

#CONFIG
st.set_page_config(page_title="Use Case", layout="wide")

#LLM
@st.cache_resource
def load_llm():
    return Ollama(model="llama3:latest")

llm = load_llm()

#SESSION STATE
if "stage" not in st.session_state:
    st.session_state.stage = "login"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

#AGENTS

# Bell (Customer Assistant)
bell_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""You are 'Bell', a helpful and empathetic AI Assistant for RLA Insurance.
You are helping Mr. Smith lodge an income protection claim.

Keep your answers concise and polite.
Guide him to provide his policy number and upload medical documents.

Current Conversation:
{history}
Human: {input}
Bell:"""
)

bell_chain = ConversationChain(
    llm=llm,
    memory=st.session_state.memory,
    prompt=bell_prompt
)

# ClaimsXpert
def claims_xpert_analyze(text_content):
    xpert_prompt = PromptTemplate.from_template(
        """You are 'ClaimsXpert', an AI assistant for RLA Insurance Case Managers.

Review the extracted claim document text and:
- Summarize the injury/illness
- Mention recommended rest period
- Flag missing information

Document Text:
{text}

Summary:"""
    )
    chain = xpert_prompt | llm
    return chain.invoke({"text": text_content})


# PDF text extraction
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text


#UI
st.title("RLA Insurance")

#STAGE 1: LOGIN
if st.session_state.stage == "login":
    st.subheader("Login and Authentication")
    st.write("Welcome, Mr. Smith. Please verify your identity.")

    otp_mobile = st.text_input("Enter OTP sent to mobile:", type="password")
    otp_email = st.text_input("Enter OTP sent to Email:", type="password")

    if st.button("Verify and Login"):
        if otp_mobile and otp_email:
            st.success("Authentication Successful")
            st.session_state.stage = "chat"
            st.rerun()
        else:
            st.error("Please enter both OTPs")

#STAGE 2: CHAT 
elif st.session_state.stage == "chat":
    st.subheader("Chat with Bell")

    # Show chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message (e.g., 'I need to lodge a claim')"):
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Bell response
        with st.chat_message("assistant"):
            with st.spinner("Bell is typing..."):
                response = bell_chain.predict(input=prompt)
                st.markdown(response)

        # Save response
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    st.divider()

    if st.button("Proceed to Document Upload"):
        st.session_state.stage = "upload"
        st.rerun()

#STAGE 3: UPLOAD
elif st.session_state.stage == "upload":
    st.subheader("Document Upload")
    st.write("Please upload your claim and medical documents.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is not None:
        st.success(f"{uploaded_file.name} uploaded successfully!")

    if st.button("Submit Claim"):
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.stage = "assessment"
            st.rerun()
        else:
            st.error("Please upload a document before submitting.")

#STAGE 4: ASSESSMENT
elif st.session_state.stage == "assessment":
    st.subheader("Case Manager View")
    st.info("The claim has been routed to Case Manager Dan.")

    with st.spinner("Analyzing document..."):
        document_text = extract_text_from_pdf(st.session_state.uploaded_file)
        analysis_result = claims_xpert_analyze(document_text)

    st.success("Analysis Complete")

    st.markdown("### ClaimsXpert Summary Report")
    st.write(analysis_result)

    st.divider()

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()