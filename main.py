import streamlit as st
import nltk
nltk.download('stopwords')
import joblib
import time
import numpy as np
from collections import defaultdict
from text_cleaning import preprocess_texts
from live_chat import get_live_chat_id, get_live_chat_messages

# --- Load model and labels ---
pipeline = joblib.load("artifacts/final_model.pkl")
labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

# --- Session state for stopping infinite loop and label counts ---
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'label_counts' not in st.session_state:
    st.session_state.label_counts = defaultdict(int)

def classify_comment(text):
    cleaned = preprocess_texts([text])[0]
    prediction = pipeline.predict([cleaned])[0]
    if isinstance(prediction, (int, float, bool, np.integer)):
        return [labels[0]] if prediction == 1 else []
    return [label for label, val in zip(labels, prediction) if val == 1]

def stream_chat(video_id):
    chat_id = get_live_chat_id(video_id)
    if not chat_id:
        return None, "❌ No live chat found for this video."

    st.success("✅ Connected to live chat. Streaming messages...")
    placeholder = st.empty()
    count_placeholder = st.sidebar.empty()
    all_flagged = []
    next_token = None

    while st.session_state.monitoring:
        messages, next_token = get_live_chat_messages(chat_id, next_token=next_token, max_messages=20)
        for ts, user, msg in messages:
            predicted = classify_comment(msg)
            print(f"[{ts}] {user}: {msg}")  # ✅ Print all messages to terminal
            if predicted:
                print(f"🚨 TOXIC [{ts}] {user}: {msg} → {predicted}")  # ✅ Print toxic flagged ones
                for label in predicted:
                    st.session_state.label_counts[label] += 1
                all_flagged.append((ts, user, msg, predicted))
                placeholder.markdown(f"**[{ts}] {user}**: {msg} → `{predicted}`")

        # Update sidebar live counts
        count_placeholder.markdown("### 🔢 Toxic Label Counts (Live)")
        for label in labels:
            count = st.session_state.label_counts[label]
            count_placeholder.markdown(f"- **{label}**: {count}")

        time.sleep(1)
    return all_flagged, None

# --- Streamlit UI ---
st.title("📺 YouTube Live Toxic Comment Monitor")
st.write("This app monitors live chat messages from a YouTube livestream and flags toxic content in real time.")

video_id = st.text_input("Enter YouTube Live Video ID (e.g. u4jOPTUQqpo):")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("▶️ Start Monitoring"):
        if video_id:
            st.session_state.monitoring = True
            st.session_state.label_counts = defaultdict(int)  # reset on new run
        else:
            st.warning("Please enter a valid video ID.")

with col2:
    if st.button("⏹️ Stop Monitoring"):
        st.session_state.monitoring = False

if st.session_state.monitoring and video_id:
    stream_chat(video_id)