import streamlit as st
from openai import OpenAI
import base64
from PIL import Image

st.set_page_config(page_title="Pictogram Chat", layout="wide")
st.title("🖼️ Pictogram Chat Assistant")
st.caption("Upload an image and chat with AI to extract information from it.")

# --- Sidebar UI for API key and uploaded image ---
with st.sidebar:
    st.header("🔧 Settings")
    api_key = st.text_input("OpenAI API Key", type="password")

    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

# --- Session State Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Function to encode image to base64 ---
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# --- Store image base64 once ---
if uploaded_image and "base64_image" not in st.session_state:
    uploaded_image.seek(0)
    st.session_state.base64_image = encode_image_to_base64(uploaded_image)

# --- Display prompt history in sidebar ---
with st.sidebar:
    st.markdown("### 📝 Previous Questions")
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"**{i+1}.** {message['content'][0]['text']}")

# --- Main Chat Interface ---
st.markdown("### 💬 Ask your question about the image:")
user_prompt = st.text_input("Type your question", key="chat_input")

# --- Send button ---
if st.button("Send", use_container_width=True) and user_prompt and uploaded_image and api_key:
    # Append user prompt to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": [
            {"type": "input_text", "text": user_prompt},
            {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{st.session_state.base64_image}",
            },
        ]
    })

    try:
        # Create OpenAI client
        client = OpenAI(api_key=api_key)

        # Send to GPT-4 Vision
        response = client.responses.create(
        model="gpt-4.1",
        input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{encode_image_to_base64(uploaded_image)}",
                        },
                    ],
                }
            ],
        )

            # Display response
        st.markdown("### ImageGPT Response")
        assistant_reply = response.output_text
        #st.write(assistant_reply)  

        # Append assistant reply to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_reply,
        })

    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# --- Display full conversation like ChatGPT ---
if st.session_state.chat_history:
    st.markdown("### 🧠 Conversation")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**🧑 You:** {message['content'][0]['text']}")
        elif message["role"] == "assistant":
            st.markdown(f"**🤖 GPT-4:** {message['content']}")

