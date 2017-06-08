#!/usr/bin/env python
 
from bs4 import BeautifulSoup
from nltk.tag import StanfordNERTagger
from random import random
import requests
import os
import sys
import subprocess
import rdflib

source_dir = os.path.dirname(__file__)
knowledge_graph = "reverbDB.ttl"
ner = StanfordNERTagger('english.all.3class.caseless.distsim.crf.ser.gz')
prefix = "prefix reverbDB: <reverbDB:>"

def import_strings(fn):
    commands = []
    strings_dir = os.path.dirname(__file__) + "/../data/strings/"
    with open(strings_dir + fn, "r") as f:
        for line in f:
            commands.append(line.strip())
    return commands

question_words = import_strings("questions.txt")


def get_entities(s):
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

def load_kg():
    ttl_file = source_dir + "/../data/ontologies/" + knowledge_graph
    g = rdflib.Graph()
    g.parse(ttl_file, format="ttl")
    print(g)

def quora(query):
    cleaned = sanitize(query, "-")
    url = 'https://www.quora.com/' + cleaned

    # print("Requesting data from {0}".format(url))
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    paragraphs = soup.find_all("p")

    html = [] 
    for p in paragraphs:
        html.append(p.decode_contents(formatter="html").replace("&nbsp;",""))
#    print("This is what I found:")
#    print(html)

    response = ""
    for index, line in enumerate(html):
        if "<" in line:
            continue
        if index > 3:
            break
        response = " ".join([response, line])

    return response


def reverb(query):
    query = query.replace("?", "")
    entity = get_entities(query)
    entity_norm = entity.strip().replace(" ", "_")
    prefix = "prefix reverbDB: <reverbDB:>"
    sparql_query = "\n".join([prefix, "select ?p ?o where {reverbDB:" + entity_norm + " ?p ?o} limit 10000"])
    print(sparql_query)
    try:
        response = subprocess.check_output(["bash", source_dir + "/../sparql/sparql.sh", sparql_query]).decode('utf-8')
    except:
        return("Error with SPARQL Query")
    lines = parse_sparql_output(response)
    return " and ".join(["{0} {1}\n".format(entity.strip(), line.strip()) for line in lines.split("\n")])

def parse_sparql_query(q):
    for idx, word in enumerate(question_words):
        q = q.replace(word, "?{0}".format(random()))

    if "and" in q:
        response = handle_multi_part_query(q)

    return response


def handle_multi_part_query(q):
    q = q.split("and")
    entity = get_entities(q[0])
    if entity:
        sparql_query = "\n".join([prefix, "select ?w where { ?w {0} {1}".format(p, o)])


def respond(q):
    print(q)
    if "describe" in q:
        return reverb(q)
    elif "who" in q:
        return sparql(q)
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
