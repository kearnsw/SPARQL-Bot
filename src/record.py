#!/usr/bin/env python

import speech_recognition as sr

# obtain path to "english.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")

def listen():
    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.Microphone(device_index=4) as source:
            print("Say something!")
            audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    try:
        print("sending request")
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio. Try again.")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == "__main__":
    print(record())
