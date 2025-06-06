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

st.title("📝 Auto-Summary Tool")
st.write("Paste a URL or article text below and get a quick summary.")

input_text = st.text_area("Paste article URL or text")

if st.button("Summarize"):
    with st.spinner("Summarizing..."):
        if input_text.startswith("http"):
            article = fetch_article_text(input_text)
            summary = summarize_text(article)
        else:
            summary = summarize_text(input_text)
        st.subheader("Summary")
        st.write(summary)
