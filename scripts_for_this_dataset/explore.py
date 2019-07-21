#!/usr/bin/env python
# Some simple scripts to explore the dataset

from __future__ import print_function, division

import os
import glob
import sys

from collections import Counter

folders = glob.glob('../dataset/experiment*')
print("Folders found:", len(folders))

# Get all the annotations
annotations = {}
for folder in folders:
    with open(os.path.join(folder, "anomaly_labels.txt"), "r") as fd:
        lines = fd.readlines()
        lines = tuple([x.strip() for x in lines])
        if lines not in annotations:
            annotations[lines] = []
        annotations[lines].append(folder)

# Print some stats on the annotations
for k, v in annotations.iteritems():
    print(len(v), k)

# Count the annotations
unique_annotations = Counter()
for k in annotations.iterkeys():
    for x in k:
        unique_annotations[x] += 1
print("Unique annotations:", unique_annotations)
