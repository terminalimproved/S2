import os
import asyncio
import edge_tts
import pygame
import tempfile
import speech_recognition as sr
from groq import Groq

# Initialize the Groq client with the API key
client = Groq(api_key="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")
pygame.mixer.init()
recognizer = sr.Recognizer()

async def chat_and_speak():
    while True:
        # Use speech recognition to capture audio from the microphone
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            print("Processing...")

            # Recognize speech using Google Web Speech API
            try:
                prompt = recognizer.recognize_google(audio)
                print("USER:", prompt)
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                continue

        # Chatbot response using Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        
        chatbot_response = chat_completion.choices[0].message.content

        # Convert text to audio
        TEXT = chatbot_response
        VOICE = "en-GB-SoniaNeural"

        # Create a temporary audio file for the response
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            OUTPUT_FILE = temp_audio_file.name

        # Use edge_tts to generate audio
        communicate = edge_tts.Communicate(TEXT, VOICE)
        await communicate.save(OUTPUT_FILE)

        # Load and play the audio file using pygame
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(1)

        # Clean up
        pygame.mixer.music.unload()
        os.remove(OUTPUT_FILE)

async def transcribe_audio():
    # Specify the path to the audio file for transcription
    filename = os.path.dirname(__file__) + "/sample_audio.m4a"  # Replace with your audio file!

    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),  # Required audio file
            model="distil-whisper-large-v3-en",  # Required model to use for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            language="en",  # Optional
            temperature=0.0  # Optional
        )
        # Print the transcription text
        print("Transcription:", transcription.text)

# Run the asynchronous functions
async def main():
    await asyncio.gather(chat_and_speak(), transcribe_audio())

asyncio.run(main())
