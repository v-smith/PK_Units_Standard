import csv
import pk_aug.augmentation as pk_aug
from collections import Counter
import pandas as pd

with open("../data/dictionaries/original_output_freqs.csv", newline='') as f:
    reader = csv.reader(f)
    original_mentions_all = list(reader)

standardised_mentions = []
for mention in original_mentions_all[1:]:
    standard_units = pk_aug.standardise_unit(mention[1])
    numerator, denominator = pk_aug.standardise_divide(standard_units)
    standardised_mentions.append({"original mention": mention[1], "standardised numerator": numerator, "standardised denominator": denominator, "frequency": mention[2]})

pd.DataFrame(standardised_mentions).to_csv("../data/dictionaries/standard_output_frequencies")

