from record import listen 
from answer import quora, reverb
from talk import speak
import argparse
import os

def parse_args():
    cli_args = argparse.ArgumentParser()
    cli_args.add_argument('-t', '--text', action='store_true', help='run with text input only')
    cli_args.add_argument('-m', '--no-sound', dest='mute', action='store_true', help='output text instead of audio')
    return cli_args.parse_args()

def import_strings():
    commands = []
    strings_dir = os.path.dirname(__file__) + "/../data/strings/"
    with open(strings_dir + "exit.txt", "r") as f:
        for line in f:
            commands.append(line.strip())
    return commands

if __name__ == "__main__":
    
    args = parse_args()
    exit_commands = import_strings()

    while True:
        query = None    
        answer = None

        if args.text:
            # Take text input from stdin
            query = input("λ > ")
        else:
            # Listen for user audio input
            query = listen()
        
        # Check if the user wants to end the session
        if any(word in query.lower() for word in exit_commands):
                break
        
        # Answer user query
        answer = reverb(query)
        if not answer:
            answer = 'Sorry, I could not find the answer to the question: "{0}".'.format(query)

        # Send the answer using either text or audio
        if args.mute:
            print(answer)
        else:
            speak(answer)

