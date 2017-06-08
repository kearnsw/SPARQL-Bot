#!/usr/bin/env python
 
from bs4 import BeautifulSoup
from nltk.tag import StanfordNERTagger
import requests
import os
import sys
import subprocess
import re

source_dir = os.path.dirname(__file__)
knowledge_graph = "reverbDB.ttl"
ner = StanfordNERTagger('english.all.3class.caseless.distsim.crf.ser.gz')

if "DATABASE" not in os.environ.keys():
    os.environ["DATABASE"] = "test"

if os.environ["DATABASE"] == "reverb":
    prefix = ""
else:
    prefix = "prefix reverbDB: <reverbDB:>"


def import_strings(fn):
    """
    Read string file
    :param fn: input file name
    :return: list of strings
    """
    commands = []
    strings_dir = os.path.dirname(__file__) + "/../data/strings/"
    with open(strings_dir + fn, "r") as f:
        for line in f:
            commands.append(line.strip())
    return commands

question_words = import_strings("questions.txt")


def get_entities(s):
    """
    Use Stanford NER to extract entities from a string
    :param s: a string
    :return: an entire named entity as string
    """
    tags = ner.tag(s.split())
    entity = ""
    for tag in tags:
        if tag[1] != "O":
            entity = " ".join((entity, tag[0]))
    return entity


def sanitize(text, replace_char):
    chars_to_remove = [" ", "'", '"', '?', '.']
    for char in chars_to_remove:
        text = text.replace(char, replace_char)
    return text


def quora(query):
    cleaned = sanitize(query, "-")
    url = 'https://www.quora.com/' + cleaned

    # print("Requesting data from {0}".format(url))
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    paragraphs = soup.find_all("p")

    html = [] 
    for p in paragraphs:
        html.append(p.text.replace("&nbsp;",""))
    response = ""
    for index, line in enumerate(html):
        if "<" in line:
            continue
        if index > 5:
            break
        response = " ".join([response, line])
    if response:
        return response
    else:
        return "Sorry, I couldn't find an answer to your question {0}".format(query)

def describe(query):
    """
    Runs a SPARQL query to pull all predicate object pairs for a given entity
    :param query: user query
    :return: natural language response
    """
    query = query.replace("?", "")
    entity = get_entities(query)
    entity_norm = entity.strip().replace(" ", "_")
    sparql_query = "\n".join([prefix, "select ?p ?o where {reverbDB:" + entity_norm + " ?p ?o} limit 10000"])
    print(sparql_query)
    try:
        response = subprocess.check_output(["bash", source_dir + "/../sparql/sparql.sh", sparql_query]).decode('utf-8')
    except:
        return("Error with SPARQL Query")
    lines = parse_sparql_output(response)
    return " and ".join(["{0} {1}\n".format(entity.strip(), line.strip()) for line in lines.split("\n")])


def parse_sparql_query(q):
    """
    Determines what form of SPARQL query the user input requires and then runs the appropriate parser
    :param q: user query
    :return: natural language form of the SPARQL results
    """
    original = q
    for idx, word in enumerate(question_words):
        q = q.replace(word, "?{0}".format(idx))
    if "and" in q.split():
        sparql_query = handle_multi_part_query(q)
    else:
        s,p,o = get_triple(q)
        sparql_query = "\n".join([prefix, "select ?w where {{ ?w {0} {1} .}}".format(p, o)])

    answer = run_sparql_query(sparql_query)
    if answer:
        return "{0} {1}".format(answer, re.sub("\?[0-9]+", "", q))
    else:
        return quora(original)


def handle_multi_part_query(q):
    """
    Handler for questions that require construction with a semicolon
    :param q: user query containing "and" keyword
    :return: SPARQL query
    """
    q = q.split("and")
    s,p,o = get_triple(q[0])
    sparql_query = "\n".join([prefix, "select ?w where {{ ?w {0} {1} ;\n".format(p, o)])
    for idx, part in enumerate(q[1:]):
        part = part.split()
        p = "reverbDB:" + "_".join(part[0:-1])
        o = "reverbDB:" + part[-1]
        if idx == len(q[1:]) - 1:
            sparql_query += "\t {0} {1} .}}".format(p, o)
        else:
            sparql_query += "\t {0} {1} ;".format(p, o)
    return sparql_query


def run_sparql_query(sparql_query):
    print(sparql_query)
    try:
        response = subprocess.check_output(["bash", source_dir + "/../sparql/sparql.sh", sparql_query]).decode('utf-8').strip()
    except:
        return("Error with SPARQL Query")

    lines = parse_sparql_output(response)
    return " and ".join(["{0} ".format(line.strip()) for line in lines.split("\n")]).strip()

def get_triple(query):
    entity = get_entities(query).strip()
    if entity:
        query = query.replace(entity, entity.replace(" ", "_"))
    query = query.split()
    s = "reverbDB:" + query[0]
    p = "reverbDB:" + "_".join(query[1:-1])
    o = "reverbDB:" + query[-1]
    return s,p,o


def respond(q):
    if "describe" in q:
        return describe(q)
    elif any(word in q for word in question_words):
        return parse_sparql_query(q)
    else:
        return quora(q)


def parse_sparql_output(response):
    output = []
    for line in response.split("\n"):
        line = line.replace("|", "").strip()
        if "reverbDB" in line:
            line = line.split()
            for element in line:
                element = element.split(":")[1]
                output.append(element.replace("_", " "))
            output.append("\n")
    return " ".join(output).strip()

if __name__ == "__main__":
    query = sys.argv[1]
