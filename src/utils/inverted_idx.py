import pandas as pd
import rdflib
import sys
from collections import defaultdict
import pickle

data =pd.read_csv(sys.argv[1], delimiter="\t", names=["id", "arg1", "pred", "arg2", "arg1_norm", "pred_norm", "arg2_norm", "count", "confidence", "urls"])

inverted_idx = defaultdict(list)

for idx, row in data.iterrows():
    sentence = " ".join((str(row["arg1"]), str(row["pred"]), str(row["arg2"])))
    for word in sentence.lower().split():
        inverted_idx[word].append(row["id"])

print(len(inverted_idx["england"]))
print(len(inverted_idx.keys()))
with open("inverted_idx.pkl", "wb") as f: 
    pickle.dump(inverted_idx, f)


