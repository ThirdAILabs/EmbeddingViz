# Note: We train the Amazon Kaggle Product Catalog Dataset with 110K products. For
# the purprose of this demo, we randomly sample just 5% of the products and
# build a cold-start search engine with UDT. Please download the dataset,
# extract the downloaded file and specify the filepath via command line using
# --catalog

import json
import os
import struct
from argparse import ArgumentParser
from collections import defaultdict

import numpy as np
import pandas as pd

# reload the embeddings
def main(args):
    product_embeddings = np.load(args.embed_path)

    import faiss

    nb, d = product_embeddings.shape
    labels = []

    index = faiss.IndexFlatL2(d)  # build the index

    index.add(product_embeddings)  # add vectors to the index

    # Since the element is part of the database, we want to add +1 to get n
    # neighbours, first nearest will the self-connection.
    k = args.neighbours + 1
    k = min(k, nb)

    distances, indices = index.search(product_embeddings, k)  # sanity check

    print("Example: ", distances[:5], indices[:5])

    adj = defaultdict(set)
    for u in range(nb):
        for j in range(k):
            v = int(indices[u, j])
            # No self loops, distance has to be within something.
            if v != u and distances[u, j] < args.threshold:
                adj[u].add(v)
                # adj[v].add(u)

    df = pd.read_csv(args.catalog)
    df["TITLE"] = df["TITLE"].fillna("missing-title")
    ids = df["PRODUCT_ID"].tolist()
    titles = df["TITLE"].tolist()
    pairs = zip(ids, titles)
    pairs = sorted(pairs, key=lambda x: int(x[0]))

    # metadata = dict(zip(ids, titles))
    labels = [f"{id}-{title}" for id, title in pairs]

    labels_path = os.path.join(args.output_dir, "labels.json")
    with open(labels_path, "w+") as labels_fp:
        json.dump(labels, labels_fp, indent=True, ensure_ascii=True, allow_nan=False)

    # Write out links.bin

    links_path = os.path.join(args.output_dir, "links.bin")

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
            for _v in adj[_u]:
                # print(_u, _v)
                v = _v + 1
                links_fp.write(struct.pack("<i", v))


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--embed-path",
        type=str,
        required=True,
    )

    parser.add_argument("--neighbours", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=10)
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
    )

    parser.add_argument("--catalog", type=str, required=True)
    args = parser.parse_args()
    main(args)
