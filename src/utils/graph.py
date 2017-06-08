#!/usr/bin/env python

import pandas as pd
import rdflib
import sys

data = pd.read_csv(sys.argv[1], delimiter="\t", names=["id", "arg1", "pred", "arg2", "arg1_norm", "pred_norm", "arg2_norm", "count", "confidence", "urls"])

g = rdflib.Graph()

# data = data[["arg1", "pred", "arg2"]]

def clean(s):
    s = str(s)
    chars_to_remove = ["&", "+", "=", "`", "~", "'", '"', "@", "*", "!", "#", "^", "-", "$", ",", ".", "/", "\\", "%"]
    for char in chars_to_remove:
        s = s.replace(char, "")
    s = s.replace(" ", "_").lower()
    return "reverbDB:" + s

print("@prefix reverbDB: <http://www.kearnsw.com/> .")
for idx, row in data.iterrows():
    s = clean(row["arg1"])
    p = clean(row["pred"])
    o = clean(row["arg2"])
    print("{0}\t{1}\t{2}\t.".format(s, p, o))
