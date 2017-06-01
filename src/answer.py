#!/usr/bin/env python
 
from bs4 import BeautifulSoup
import requests
import os
import sys
import subprocess

def sanitize(text):
    chars_to_remove = [" ", "'", '"']
    for char in chars_to_remove:
        text = text.replace(char, "-")
    return text

def quora(query):
    cleaned = sanitize(query)
    url = 'https://www.quora.com/' + cleaned

    print("Requesting data from {0}".format(url))
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    paragraphs = soup.find_all("p")

    html = [] 
    for p in paragraphs:
        html.append(p.decode_contents(formatter="html").replace("&nbsp;",""))
    print("This is what I found:")
    print(html)

    response = ""
    for index, line in enumerate(html):
        if "<" in line:
            continue
        if index > 3:
            break
        response = " ".join([response, line])

    return response

def reverb(query):
    source_dir = os.path.dirname(__file__)
    sparql_query = "select ?s where {?s ?p ?o} limit 10"
    response = subprocess.check_output(["bash", source_dir + "/sparql.sh", sparql_query]).decode('utf-8')
    return response

if __name__ == "__main__":
    query = sys.argv[1]
    
