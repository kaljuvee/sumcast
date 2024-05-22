import streamlit as st
import requests
import openai
from pydub import AudioSegment
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load the environment variables from the .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai.api_key)


# Function to extract audio from Spotify podcast (assuming a downloadable link is provided)
# Function to extract audio from Spotify podcast (assuming a downloadable link is provided)
def download_audio(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Error fetching audio from URL: {response.status_code}")

    # Try to determine the file format from the URL or response headers
    content_type = response.headers.get('Content-Type')
    if content_type:
        # Guess the file extension from the content type
        format_map = {
            'audio/mpeg': 'mp3',
            'audio/mp4': 'mp4',
            'audio/x-wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/webm': 'webm',
            # Add more mappings as needed
        }
        original_format = format_map.get(content_type)
        if not original_format:
            raise ValueError(f"Unsupported audio format: {content_type}")
    else:
        # Fallback if content type is not available
        original_format = 'mp3'
    
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
