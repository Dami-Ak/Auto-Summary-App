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

st.title("📝 Auto-Summary Tool")
st.write("Paste a URL or article text below and get a quick summary.")

input_text = st.text_area("Paste article URL or text")
summary = ""

if st.button("Summarize"):
    with st.spinner("Summarizing..."):
        if input_text.startswith("http"):
            article = fetch_article_text(input_text)
            summary = summarize_text(article)
        else:
            summary = summarize_text(input_text)
        st.session_state["summary"] = summary
        st.subheader("Original Summary")
        st.write(summary)

        analysis = analyze_summary(summary)
        st.subheader("🧠 Analysis of Messaging, Biases, and Blind Spots")
        st.write(analysis)

if "summary" in st.session_state and st.session_state["summary"]:
    st.subheader("Try Different Summary Styles")
    styles = {
        "Like I'm 5": "Explain this summary like I'm 5 years old",
        "More Detailed": "Make this summary more detailed",
        "Playful": "Rewrite this summary in a playful tone",
        "Presentation": "Turn this summary into a 5-slide presentation outline"
    }

    col1, col2, col3, col4 = st.columns(4)
    buttons = [col1.button("Like I'm 5"), col2.button("More Detailed"), col3.button("Playful"), col4.button("Presentation")]
    labels = list(styles.keys())

    for idx, pressed in enumerate(buttons):
        if pressed:
            label = labels[idx]
            instruction = styles[label]
            rewritten = rewrite_summary(st.session_state["summary"], instruction)
            st.markdown(f"**{label} Version:**")
            st.markdown(f"**Original:**\n{st.session_state['summary']}")
            st.markdown(f"**Updated:**\n{rewritten}")
