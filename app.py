import streamlit as st
import requests
import openai
from pydub import AudioSegment
import os
from openai import OpenAI

# Set OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

client = OpenAI(api_key=openai.api_key)


# Function to extract audio from Spotify podcast (assuming a downloadable link is provided)
def download_audio(url):
    response = requests.get(url)
    original_format = url.split('.')[-1]
    if original_format not in ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']:
        raise ValueError(f"Unsupported audio format: {original_format}")
    filename = f'podcast.{original_format}'
    with open(filename, 'wb') as f:
        f.write(response.content)
    if original_format != 'mp3':
        audio = AudioSegment.from_file(filename, format=original_format)
        filename = 'podcast.mp3'
        audio.export(filename, format='mp3')
    return filename

# Function to convert audio to text using Whisper
def audio_to_text(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription['text']

# Function to summarize text using OpenAI GPT-4
def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text: {text}"}
        ],
        max_tokens=150,
        n=1,
        temperature=0.7,
    )
    summary = response.choices[0].message['content'].strip()
    return summary

# Streamlit app
st.title("Podcast Summarizer")

# Step 1: Accept Spotify podcast link
podcast_url = st.text_input("Enter Spotify podcast URL")

# Add a submit button
if st.button("Submit"):
    if podcast_url:
        # Step 2: Download and convert to text
        audio_file = download_audio(podcast_url)
        st.audio(audio_file)
        text = audio_to_text(audio_file)
        st.write("Transcribed Text:", text)

        # Step 3: Summarize the text
        summary = summarize_text(text)
        st.write("Summary:", summary)
    else:
        st.write("Please enter a valid podcast URL.")
