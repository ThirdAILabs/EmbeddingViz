# Note: We train the Amazon Kaggle Product Catalog Dataset with 110K products. For
# the purprose of this demo, we randomly sample just 5% of the products and
# build a cold-start search engine with UDT. Please download the dataset,
# extract the downloaded file and specify the filepath via command line using
# --catalog_path

import json
import os
import struct
from argparse import ArgumentParser, Namespace
from collections import defaultdict

from tqdm import tqdm
import numpy as np
import pandas as pd

from generate_adjacency_list import generate_adj_list

# reload the embeddings


def generate_label_data(df, strong_column_names, target_name):
    for column in strong_column_names:
        df[column] = df[column].fillna(f"missing value for {column} entry")

    label_data = []
    for index, row in df.iterrows():
        datum = str(row[target_name])
        for column in strong_column_names:
            datum += f"-{row[column]}"
        label_data.append(datum)

    return label_data


def save_adj_list(adjacency_list, neighbours,  output_dir):
    nb = neighbours

    import pickle

    adj_path = os.path.join(output_dir, "adj_list.pickle")
    with open(adj_path, "wb") as f:
        pickle.dump(adjacency_list, f)

    links_path = os.path.join(output_dir, "links.bin")

    # links.bin content (in numerical view, spaces are just for formatting):
    # Each record in the file is Int32 written in little-endian notation.
    #
    #        -1 2 3 -2 4
    #
    # The negative 1 identifies the first "source" node of the graph, and
    # denotes 1 based index of the element in the labels.json file. So in
    # this case it is node a.   Following positive integers 2 and 3 mean
    # that a is connected to labels[2 - 1] and labels[3 - 1]. That is nodes
    # b and c correspondingly.
    #
    # Following positive integers 2 and 3 mean that a is connected to
    # labels[2 - 1] and labels[3 - 1]. That is nodes b and c
    # correspondingly.  Then we see -2. This means that there are no more
    # connections for the node a, and we should consider node labels[2 - 1]
    # as the next "source" node.
    #
    # Subsequent positive integers show connections for the node b. It is
    # node d (labels[4 - 1]).
    with open(links_path, "wb+") as links_fp:
        for _u in range(nb):
            u = _u + 1
            links_fp.write(struct.pack("<i", -1 * u))
            for _v in adjacency_list[_u]:
                # print(_u, _v)
                v = _v + 1
                links_fp.write(struct.pack("<i", v))


def generate_graph(args):

    df = pd.read_csv(args.catalog_path)

    # metadata = dict(zip(ids, titles))
    labels = generate_label_data(
        df, args.strong_column_names, args.target_name)

    labels_path = os.path.join(args.output_dir, "labels.json")
    with open(labels_path, "w+") as labels_fp:
        json.dump(labels, labels_fp, indent=True,
                  ensure_ascii=True, allow_nan=False)

    adjacency_list = generate_adj_list(args)
    save_adj_list(adjacency_list=adjacency_list,
                  neighbours=args.neighbours, output_dir=args.output_dir)


def generate_graph_from_config(config_path):
    with open(config_path, "r") as f:
        config_data = json.load(f)
        args = Namespace(**config_data)
    process_args(args)
    print(args)
    generate_graph(args)


def process_args(args):
    args.output_dir = os.path.join(args.output_dir, "v"+str(args.version))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--embed_path",
        type=str,
        required=True,
    )

    parser.add_argument("--neighbours", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=10)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--version", type=str, required=True)
    parser.add_argument("--catalog_path", type=str, required=True)
    parser.add_argument("--strong_column_names",
                        nargs="+", type=str)
    parser.add_argument("--target_name", type=str, required=True)

    args = parser.parse_args()
    process_args(args)

    print(args)
    generate_graph(args)
