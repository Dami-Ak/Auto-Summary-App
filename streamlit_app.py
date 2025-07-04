import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os

# Set your OpenAI key securely from Streamlit secrets or environment
openai.api_key = os.getenv("OPENAI_API_KEY", "")

def fetch_article_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text[:7000]  # Truncate to avoid token limit
    except Exception as e:
        return f"Error fetching article: {e}"

def summarize_text(text):
    try:
        client = openai.OpenAI()
        prompt = f"Summarize the following text clearly and concisely:\n\n{text}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error summarizing text: {e}"

def rewrite_summary(summary, instruction):
    try:
        client = openai.OpenAI()
        prompt = f"{instruction}:\n\n{summary}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error rewriting summary: {e}"

def analyze_summary(summary):
    try:
        client = openai.OpenAI()
        prompt = f"Analyze the following summary. Identify the messaging, any possible biases, and blind spots in the article:\n\n{summary}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing summary: {e}"

def detect_content_type(text):
    try:
        client = openai.OpenAI()
        prompt = f"Classify the following text into one of the content types: News, Opinion, Research, Blog, or Other. Provide a brief justification for your classification.\n\n{text}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error detecting content type: {e}"

st.title("📝 Auto-Summary Tool")
st.write("Paste a URL or article text below and get a quick summary.")

input_text = st.text_area("Paste article URL or text")
summary = ""

if st.button("Generate Summary"):
    with st.spinner("Summarizing..."):
        if input_text.startswith("http"):
            article = fetch_article_text(input_text)
            summary = summarize_text(article)
            content_type = detect_content_type(article)
        else:
            summary = summarize_text(input_text)
            content_type = detect_content_type(input_text)
        st.session_state["summary"] = summary
        st.session_state["analysis"] = analyze_summary(summary)
        st.session_state["content_type"] = content_type
        st.session_state["styled_summaries"] = []

if "summary" in st.session_state and st.session_state["summary"]:
    with st.expander("📄 Original Summary", expanded=True):
        st.write(st.session_state["summary"])

    with st.expander("📚 Detected Content Type", expanded=True):
        st.write(st.session_state["content_type"])

    with st.expander("🧠 Analysis of Messaging, Biases, and Blind Spots", expanded=True):
        st.write(st.session_state["analysis"])

    st.markdown("### 🎨 Try Different Summary Styles")
    styles = {
        "Explain Like I'm 5": "Explain this summary like I'm 5 years old",
        "More Detailed": "Make this summary more detailed",
        "Playful": "Rewrite this summary in a playful tone",
        "5-Slide Presentation Outline": "Turn this summary into a 5-slide presentation outline"
    }

    for label, instruction in styles.items():
        if st.button(label):
            with st.spinner(f"Rewriting summary: {label}..."):
                rewritten = rewrite_summary(st.session_state["summary"], instruction)
            st.session_state["last_style"] = (label, rewritten)

    if "last_style" in st.session_state:
        label, rewritten = st.session_state["last_style"]
        with st.expander("✨ Styled Summary", expanded=True):
            st.markdown(f"**{label}:**")
            st.markdown(rewritten)
