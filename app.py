from io import StringIO
import streamlit as st
import json

from codeChecker import codeChecker


st.set_page_config(page_title="Interactive AI Debugger", layout="wide")
st.title("code checker")

# Session state to hold conversation history
if "history" not in st.session_state:
    st.session_state.history = []
if "tools" not in st.session_state:
    st.session_state.tools = {}

if len(st.session_state.tools) == 0:
    st.session_state.tools["checker"] = codeChecker("sk-a20fe5cabaac4bcda4af0347d3ad5038", "https://api.deepseek.com")
    
checker: codeChecker = st.session_state.tools["checker"]


def readFile(uploaded_file):
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    return stringio.read()

mode = st.segmented_control("mode: ", ["runtime", "syntax", "logical", "style", "explanation", "chat"], default="chat")

prompt = st.chat_input(
    "Say something and/or attach an file",
    accept_file=True,
    file_type=["txt", "py", "java"],
)

newPrompt = False
code = ""
if prompt and prompt.text:
    newPrompt = True
    st.session_state.history.append(
        {"role" : "user", "format" : "code" if mode != "chat" and not prompt["files"] else "text", "content" : prompt.text})
    code = prompt.text
if prompt and prompt["files"]:
    newPrompt = True
    if prompt["files"] is not None:
        code = readFile(prompt["files"][0])
        st.session_state.history.append({"role" : "user", "format" : "code", "content" : code})

try:
    if newPrompt:
        isJson = False
        with st.status("analyzing..."):
            match mode:
                case "runtime":
                    response = checker.checkCommonRuntimeError(code)
                    isJson = True
                case "syntax":
                    response = checker.checkSyntaxError(code) 
                    isJson = True
                case "logical":
                    response = checker.AlBasedLogicErrorDetection(code)
                    isJson = True
                case "style":
                    response = checker.checkStyleViolation(code)
                    isJson = True
                case "explanation":
                    response = checker.lineByLineAIExplanation(code)
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : response})
                case "chat":
                    response = checker.InteractiveDebugging(code)
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : response})
            if isJson:
                response = json.loads(response)
                lines = code.splitlines()
                checks = response["checks"]
                for check in checks:
                    if len(check) != 3:
                        continue
                    index = check["range"][0]
                    st.session_state.history.append({"role" : "bot", "format" : "code", "content" : f"{index}: " + lines[index - 1]})
                    advice = check["advice"]
                    errorType = check["errorType"]
                    st.session_state.history.append({"role" : "bot", "format" : "text", "content" : f":red[{errorType}!] :orange[advice:] :green[{advice}]"})
                    
                st.session_state.history.append({"role" : "bot", "format" : "text", "content" : "correction:"})

                correctedCode = response["correction"]
                st.session_state.history.append({"role" : "bot", "format" : "code", "content" : correctedCode})
                
                checker.setupConversation(code, correctedCode)
    lastRole = None
    for message in st.session_state.history:
        if lastRole !=message["role"]:
            st.markdown("---")
            st.markdown(":blue[user:]" if message["role"] == "user" else ":green[bot:]")
        lastRole = message["role"]
        content = message["content"]
        match message["format"]:
            case "code":
                st.code(f"{content}")
            case "text":
                st.markdown(f"{content}")
except:
    st.markdown(":red[The server is busy. Please try again later.]")