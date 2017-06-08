from talk import speak
from record import listen
from answer import respond, get_entities, get_triple
import subprocess
import argparse
import os
import re

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


def store_triples(q):
    if "and" in q.split():
        q = q.split("and")
        s, p, o = get_triple(q[0])
        store_triple(s, p, o)

        for part in q[1:]:
            part = part.split()
            p = "reverbDB:" + "_".join(part[0:-1])
            o = "reverbDB:" + part[-1]
            store_triple(s, p, o)

    elif "type" in q.split():
        entity = get_entities(q).strip()
        if entity:
            q = q.replace(entity, entity.replace(" ", "_"))
        q = q.split()
        s = "reverbDB:" + q[0]
        p = "rdf:type"
        o = "reverbDB:" + q[-1]
        store_triple(s, p, o)

    else:
        s, p, o = get_triple(q)
        store_triple(s, p, o)


def store_triple(s, p, o):
    triple = "{0}\t{1}\t{2}\t.".format(s, p, o)
    print(triple)
    subprocess.call(["bash", source_dir + "/../sparql/add.sh", triple])


def remove_triple(s, p, o):
    triple = "{0}\t{1}\t{2}\t.".format(s, p, o)
    print(triple)
    subprocess.call(["bash", source_dir + "/../sparql/remove.sh", triple])

if __name__ == "__main__":
    
    args = parse_args()

    exit_commands = import_strings("exit.txt")
    greetings = import_strings("greetings.txt")
    add_commands = import_strings("add.txt")
    question_commands = import_strings("questions.txt")
    remove_commands = import_strings("remove.txt")

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
        if any(word in query for word in exit_commands):
            speak("Goodbye")
            break
       
        # Check for greeting
        elif any(word in query.split() for word in greetings):
            answer = "Hi! I can help you manage and query a Spark Ul database." \
                     "To add an triple just begin a phrase with the keyword add"
        
        # Check if user wants to add knowledge to graph
        elif any(word in query for word in add_commands):
            for cmd in add_commands:
                query = re.sub(cmd, "", query)
            speak("I heard that you wanted to add {0}, is that correct?".format(query))
            while not user_response:
                if args.text:
                    user_response = input("λ > ")
                else:
                    user_response = listen()

            if re.search(r"yes", user_response.lower()):
                store_triples(query)
                speak("Ok, I've added that to your {0} database.".format(os.environ["DATABASE"]))
            else:
                speak("I'm sorry, can you please repeat the command?")
            continue

        # Check if user wants to remove knowledge from graph
        elif any(word in query for word in remove_commands):
            for cmd in remove_commands:
                query = re.sub(cmd, "", query)
            speak("Are you sure you want to remove {0}? this cannot be undone.".format(query))
            while not user_response:
                if args.text:
                    user_response = input("λ > ")
                else:
                    user_response = listen()

            if re.search(r"yes", user_response.lower()):
                s, p, o = get_triple(query)
                remove_triple(s, p, o)
                speak("Ok, I've removed that from your {0} database.".format(os.environ["DATABASE"]))
            else:
                speak("I'm sorry, can you please repeat the command?")
            continue

        # Answer user query
        elif any(word in query for word in question_commands):
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
