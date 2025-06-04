from io import StringIO
import streamlit as st
import json

from codeChecker import codeChecker

if __name__ == "__main__":
    checker = codeChecker("sk-a20fe5cabaac4bcda4af0347d3ad5038", "https://api.deepseek.com")
    

# Title of the app
st.title("code checker")
if "chat" not in st.session_state:
    st.session_state.chat = []
    
# Text input
st.text("\n input your code:")
code = st.text_area("", height=300)

uploaded_file = st.file_uploader("upload file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    code = stringio.read()

#display input code
st.text("your code:")
st.code(code)

errorType = st.segmented_control("error type", ["runtime", "syntax", "logical"], default="syntax")

st.write("checking for " + errorType)

response = ""
#start debugging if the code isn't empty
if st.button("check") and code != "":
    with st.status("error analyzing..."):
        match errorType:
            case "runtime":
                response = checker.checkCommonRuntimeError(code)
            case "syntax":
                response = checker.checkSyntaxError(code) 
            case "logical":
                response = checker.AlBasedLogicErrorDetection(code)   
        
    response = json.loads(response)
    lines = code.splitlines()
    checks = response["checks"]
    for check in checks:
        if len(check) != 3:
            continue
        index = check["range"][0]
        st.code(f"{index}: " + lines[index - 1])
        advice = check["advice"]
        errorType = check["errorType"]
        st.markdown(f":red[{errorType}!] :orange[advice:] :green[{advice}]")
        
    
    st.text("correction:")
    correctedCode = response["correction"]
    st.code(correctedCode)
    
    with st.status("generating explanations..."):
        response = checker.lineByLineAIExplanation(correctedCode)
        st.markdown(response)
    
    checker.setupConversation(code, correctedCode)
    user_input = st.text_input("You:", key="user_input")

    if st.button("Send"):
        if user_input.strip():
            # Add user message
            st.session_state.chat.append(("You", user_input))
            with st.status("generating response..."):
                response = checker.InteractiveDebugging(user_input)

            # Add bot response
            st.session_state.chat.append(("Bot", response))

        # Display chat
        for speaker, message in st.session_state.chat:
            st.markdown(f"**{speaker}:** {message}")