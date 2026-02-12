import streamlit as st
import pickle
import json
import random
import re
from fees import fees

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="VIT-AP AI Assistant", layout="centered")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main-card {
    background-color: #f8f9fb;
    color: blue;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
}

.bot-msg {
    background-color: #e9ecef;
    color: black;
    padding: 10px 14px;
    border-radius: 10px;
    display: inline-block;
    margin: 6px 0;
}

.user-msg {
    background-color: #1f77d0;
    color: white;
    padding: 10px 14px;
    border-radius: 10px;
    display: inline-block;
    margin: 6px 0;
    float: right;
}

.clear {
    clear: both;
}

.quick-btn button {
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
# model = pickle.load(open("model.pkl","rb"))
# vectorizer = pickle.load(open("vectorizer.pkl","rb"))
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "vectorizer.pkl")

model = pickle.load(open(model_path, "rb"))
vectorizer = pickle.load(open(vectorizer_path, "rb"))


with open("intents.json") as f:
    intents = json.load(f)

# ---------------- NLP ENTITY ----------------
def extract_program(text):
    for p in ["cse","ece","mechanical"]:
        if p in text:
            return p
    return None

def extract_category(text):
    match = re.search(r'category\s*(\d)', text)
    if match:
        return "category_" + match.group(1)
    return None

def fee_response(text):
    text=text.lower()
    program=extract_program(text)
    category=extract_category(text)

    if program and category:
        amount=fees[program][category]
        return f"{program.upper()} {category.replace('_',' ')} fee is ₹{amount}"

    if "hostel" in text:
        return "Hostel fee ranges ₹85k–₹1.2L depending on room type."

    if "mess" in text:
        return "Mess fee is ₹50,000 per year."

    return None

# ---------------- INTENT ----------------
def intent_reply(user):
    X=vectorizer.transform([user])
    tag=model.predict(X)[0]
    for intent in intents["intents"]:
        if intent["tag"]==tag:
            return random.choice(intent["responses"])

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-card">
<h2 style='text-align:center;'>🎓 VIT-AP AI Campus Assistant</h2>
<p style='text-align:center;color:gray'>
Get instant answers about admissions, fees, campus life
</p>
""", unsafe_allow_html=True)

# ---------------- CHAT MEMORY ----------------
if "history" not in st.session_state:
    st.session_state.history=[("Bot","Hello! How can I help you today?")]

# ---------------- CHAT DISPLAY ----------------
for speaker,msg in st.session_state.history:
    if speaker=="Bot":
        st.markdown(f"<div class='bot-msg'>{msg}</div><div class='clear'></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='user-msg'>{msg}</div><div class='clear'></div>", unsafe_allow_html=True)

# ---------------- INPUT ROW ----------------
col1,col2=st.columns([4,1])

with col1:
    user=st.text_input("Type your message here...", label_visibility="collapsed")

with col2:
    send=st.button("Send")

if send and user:
    fee_ans=fee_response(user)
    reply=fee_ans if fee_ans else intent_reply(user)

    st.session_state.history.append(("You",user))
    st.session_state.history.append(("Bot",reply))
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- QUICK QUESTIONS ----------------
st.markdown("### ⚡ Quick Questions")

q1,q2,q3=st.columns(3)
q4,q5,q6=st.columns(3)

if q1.button("Tuition Fee"):
    st.session_state.history.append(("You","CSE category 1 fee"))
    st.session_state.history.append(("Bot",fee_response("cse category 1")))

if q2.button("Hostel Fee"):
    st.session_state.history.append(("You","Hostel fee"))
    st.session_state.history.append(("Bot",fee_response("hostel")))

if q3.button("Admission Process"):
    st.session_state.history.append(("You","admission process"))
    st.session_state.history.append(("Bot",intent_reply("admission process")))

if q4.button("Placements"):
    st.session_state.history.append(("You","placements"))
    st.session_state.history.append(("Bot",intent_reply("placements")))

if q5.button("Scholarships"):
    st.session_state.history.append(("You","scholarship"))
    st.session_state.history.append(("Bot",intent_reply("scholarship")))

if q6.button("Campus Facilities"):
    st.session_state.history.append(("You","hostel facility"))
    st.session_state.history.append(("Bot",intent_reply("hostel")))

# ---------------- ABOUT ----------------
st.markdown("---")
st.markdown("### ℹ About this chatbot")
st.write("AI-powered assistant using NLP for student support and campus information")
