import speech_recognition as sr
from groq import Groq  # Ensure the library is configured correctly
import os
import pygame
import asyncio
import pyttsx3
import threading
from datetime import datetime

# Global variable to control the loop
running = True

# Function to initialize Pygame
def initialize_services():
    # Initialize the pygame mixer
    pygame.mixer.init()

# Function to play synthesized speech using pyttsx3
def speak(text):
    engine = pyttsx3.init()
    
    # Set the voice to Microsoft Zira (English)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name:
            engine.setProperty('voice', voice.id)
            break

    # Set the text to be spoken
    engine.say(text)
    engine.runAndWait()

# Main function to capture and recognize speech
async def main():
    global running    
    # Initializing services
    recognizer = sr.Recognizer()
    initialize_services()
    
    client = Groq(api_key="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")

    # Adjust for ambient noise once
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...") 
        recognizer.adjust_for_ambient_noise(source, duration=1)

    # Main loop to capture and process voice commands
    while running:
        with sr.Microphone() as source:
            print("Listening for command...")
            audio = recognizer.listen(source)

        # Try to recognize the text from the speech
        try:
            command = recognizer.recognize_google(audio, language='en-US')
            if not command:
                raise ValueError("Empty text recognized.")
        except sr.UnknownValueError:
            print("I couldn't understand what you said.")
            command = ""
        except sr.RequestError as e:
            print(f"Error in the recognition service request: {e}")
            command = ""

        # If there is recognized command, continue with generating a response
        if command:
            print(f"USER: {command}")

            if command.lower() == "what time is it":
                current_time = datetime.now().strftime("%H:%M")
                response = f"The current time is {current_time}."
                print(response)
                threading.Thread(target=speak, args=(response,)).start()
            elif command.lower() == "exit":
                print("Stopping the program.")
                threading.Thread(target=speak, args=("Stopping the program.",)).start()
                running = False
                break
            else:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You're a useful assistant called S1. be super-short and polite."
                            },
                            {
                                "role": "user",
                                "content": command
                            }
                        ],
                        model="llama3-8b-8192",  # Ensure the model is correct
                        temperature=0.5,
                        max_tokens=1024,
                        top_p=1,
                        stream=False
                    )

                    chatbot_response = chat_completion.choices[0].message.content
                    print(chatbot_response)

                    # Call the function to synthesize and play the response
                    threading.Thread(target=speak, args=(chatbot_response,)).start()

                except Exception as e:
                    print(f"Error processing the chatbot response: {e}")
                    threading.Thread(target=speak, args=("Sorry, but there was an error processing your request.",)).start()

# Stop function 
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
