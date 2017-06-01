#!/usr/bin/env python

from gtts import gTTS
import os
import sys
import subprocess
from time import sleep
from tempfile import NamedTemporaryFile

def speak(text):
    # Send TTS request through Google Translate API
    tts = gTTS(text=text, lang='en', slow=False) 
    
    # Play audio saving the data in a secure temporary file 
    # that is automatically deleted
    tf = NamedTemporaryFile()
    tts.save(tf.name)
    subprocess.call(["play", "-t", "mp3", tf.name])
    tf.close()

if __name__ == "__main__":
    speak(sys.argv[1])
