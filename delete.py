import pandas as pd

pitchfork_authors = pd.read_pickle("pitchfork_authors")
pitchfork_authors.to_csv("pitchfork_authors")

pitchforked_clean = pd.read_pickle("pitchforked_clean")
pitchforked_clean.to_csv("pitchforked_clean")