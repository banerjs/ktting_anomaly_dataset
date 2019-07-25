#!/usr/bin/env python
# Some simple scripts to explore the dataset

from __future__ import print_function, division

import os
import glob
import sys
import argparse

from collections import Counter
from multiprocessing import Pool

import rosbag


# Get the experiment folders
def get_data_folders(folders_glob):
    folders = glob.glob('../dataset/experiment*')
    print("Folders found:", len(folders))
    return folders


# Print stats about the annotations
def print_annotation_stats(folders):
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


# Get the bag info, because this is expensive
def get_bag_data(folder):
    # Information to return. Can be more in the future
    topics_and_message_types = {}

    bag = rosbag.Bag(os.path.join(folder, 'record.bag'), 'r')
    types, topics = bag.get_type_and_topic_info()
    for topic, topic_info in topics.iteritems():
        topics_and_message_types[topic] = topic_info[0]

    return folder, topics_and_message_types

# Iterate through the bags and print information about the msgs in the bags
def print_bag_msg_types(folders):
    topics_and_message_types = {}

    # Send off the bags to a multiprocessing pool and check the results
    pool = Pool()

    for idx, (folder, bag_data) in enumerate(pool.imap_unordered(get_bag_data, folders[1:], 20)):
        for topic, msg_type in bag_data.iteritems():
            if topic not in topics_and_message_types:
                topics_and_message_types[topic] = msg_type
            else:
                assert topics_and_message_types[topic] == msg_type, \
                    "Mismatch in {}({}): {} != {}".format(
                        folder, topic, msg_type, topics_and_message_types[topic]
                    )

        print("Processed ({}/{}):".format(idx+1, len(folders)), folder)

    pool.close()
    pool.join()

    # Print the unique list of topics and message types
    for topic, msg_type in topics_and_message_types.iteritems():
        print(topic, msg_type)


# The main part of the code
if __name__ == '__main__':
    # Create the arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-annotation-stats', action='store_true')
    parser.add_argument('--no-bag-msg-types', action='store_true')
    args = parser.parse_args()

    # Get the folders
    folders = get_data_folders(os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'dataset/experiment*'
        )
    ))

    # If we want the annotation stats
    if not args.no_annotation_stats:
        print_annotation_stats(folders)

    # If we want the bag msg types
    if not args.no_bag_msg_types:
        print_bag_msg_types(folders)
