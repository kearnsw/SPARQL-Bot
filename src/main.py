from record import listen 
from answer import respond, get_entities
from talk import speak
import subprocess
import argparse
import os


source_dir = os.path.dirname(__file__)


def parse_args():
    cli_args = argparse.ArgumentParser()
    cli_args.add_argument('-t', '--text', action='store_true', help='run with text input only')
    cli_args.add_argument('-m', '--no-sound', dest='mute', action='store_true', help='output text instead of audio')
    return cli_args.parse_args()


def import_strings(fn):
    commands = []
    strings_dir = os.path.dirname(__file__) + "/../data/strings/"
    with open(strings_dir + fn, "r") as f:
        for line in f:
            commands.append(line.strip())
    return commands

if __name__ == "__main__":
    
    args = parse_args()
    exit_commands = import_strings("exit.txt")
    greetings = import_strings("greetings.txt")
    add_commands = import_strings("add.txt")
    question_commands = import_strings("questions.txt")

    while True:
        query = None    
        answer = None
        response = None
        user_response = None

        if args.text:
            # Take text input from stdin
            query = input("λ > ")
        else:
            # Listen for user audio input
            query = listen()

        if not query:
            continue

        query = query.lower()
        
        # Check if the user wants to end the session
        if any(word in query.lower() for word in exit_commands):
                break
       
        # Check for greeting
        if any(word in query.lower() for word in greetings):
            answer = "Hi! "
        
        # Check if user wants to add knowledge to graph
        if any(word in query.lower() for word in add_commands):
            for cmd in add_commands:
                query = query.replace(cmd, "")
            speak("I heard that you wanted to add {0}, is that correct?".format(query))
            while not user_response:
                user_response = listen()

            if "yes" in user_response.lower():
                entity = get_entities(query).strip()
                if entity:
                    query = query.replace(entity, entity.replace(" ", "_"))
                query = query.split()
                s = "reverbDB:" + query[0]
                p = "reverbDB:" + "_".join(query[1:-1])
                o = "reverbDB:" + query[-1]
                print(s,p,o)
                triple = "{0}\t{1}\t{2}\t.".format(s, p, o)
                print(triple)
                subprocess.call(["bash", source_dir + "/../sparql/add.sh", triple])
                answer = "Added {0}".format(triple)
                speak("I've added that to your {0} database.".format(os.environ["DATABASE"]))

            else:
                speak("I'm sorry, can you please repeat the command?")
            continue

        # Answer user query
        if any(word in query.lower() for word in question_commands):
            response = respond(query)
        if response:
            answer = response

        # Handle an unanswerable query
        if answer is "":
            answer = 'Sorry, I could not find the answer to the question: "{0}".'.format(query)

        # Send the answer using either text or audio
        if args.mute:
            print(answer)
        else:
            speak(answer)
        
        answer = ""
        response = None
        user_response = None
