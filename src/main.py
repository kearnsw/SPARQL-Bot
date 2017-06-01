from record import listen 
from answer import quora
from talk import speak
import argparse

def parse_args():
    cli_args = argparse.ArgumentParser()
    cli_args.add_argument('-t', '--text', action='store_true', help='run with text input only')
    cli_args.add_argument('-m', '--no-sound', dest='mute', action='store_true', help='output text instead of audio')
    return cli_args.parse_args()

if __name__ == "__main__":
    
    args = parse_args()
    
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
        if "stop" in query.lower():
                break
        
        # Answer user query
        answer = quora(query)
        if not answer:
            answer = "I couldn't find the answer to the question, " + query

        # Send the answer using either text or audio
        if args.mute:
            print(answer)
        else:
            speak(answer)

