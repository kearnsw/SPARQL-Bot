#!/usr/bin/env python

from gtts import gTTS
import sys
import subprocess
from tempfile import NamedTemporaryFile

def speak(text):
    try:
        # Send TTS request through Google Translate API
        tts = gTTS(text=text, lang='en', slow=False)

        # Play audio saving the data in a secure temporary file
        # that is automatically deleted
        tf = NamedTemporaryFile()
        tts.save(tf.name)
        subprocess.call(["play", "-t", "mp3", tf.name])
        tf.close()
    except:
        print(text)
        print("TTS: received no text")

if __name__ == "__main__":
    speak(sys.argv[1])
