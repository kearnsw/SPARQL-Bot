#!/usr/bin/env python

import speech_recognition as sr
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")


def listen():
    print("I'm recording")
    r = sr.Recognizer()
    with sr.Microphone(device_index=12) as source:
            r.adjust_for_ambient_noise(source)
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
    print(listen())
