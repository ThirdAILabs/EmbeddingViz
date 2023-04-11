import os
import json
import thirdai
from thirdai import bolt
from collections import defaultdict

from tqdm import tqdm
import numpy as np
import pandas as pd


def combine_columns(df, columns_to_combine):
    df = df[columns_to_combine]
    return df.astype(str).agg(' '.join, axis=1).tolist()


def index2dArray(a, index):
    return a[np.arange(a.shape[0])[:, None], index]


def generate_query_batch(df: pd.DataFrame, query_column_name,  columns_to_combine, k_grams):
    queries = combine_columns(df, columns_to_combine)

    data = []
    for query in queries:
        if k_grams:
            query = ' '.join([query[i:i+k_grams]
                             for i in range(len(query)-k_grams+1)])
        data.append({query_column_name: query})
    return data


def num_chunks(df, batch_size=2000):
    return len(df)/batch_size + 1


def get_adj_list_from_model(args):
    # We need the following elements in args
    # 1. model_path
    # 2. catalog_path
    # 3. sparse_inference
    # 4. neighbours
    # 5. columns_to_combine
    # 6. k_grams : int or None
    # 7. query_column_name
    # 8. target_name
    # 9. undirected_edges

    model = bolt.UniversalDeepTransformer.load(args.model_path)
    data = pd.read_csv(args.catalog_path)

    print(args.model_path)
    print(args.catalog_path)

    i = 0

    if args.sparse_inference:
        print("Using sparse inference")

    adjacency_list = defaultdict(set)
    for chunk in tqdm(np.array_split(data, num_chunks(data))):
        number_queries = len(chunk)
        target_ids = chunk[args.target_name].tolist()
        query_batch = generate_query_batch(
            df=chunk,
            query_column_name=args.query_column_name, columns_to_combine=args.columns_to_combine, k_grams=args.k_grams
        )

        if i == 0:
            print(chunk[args.columns_to_combine].astype(
                str).agg(' '.join, axis=1).tolist()[0])
            print(query_batch[0])
            i = i+1

        activations = model.predict_batch(
            query_batch, sparse_inference=args.sparse_inference)

        if args.sparse_inference:
            sparse_indices = activations[0]
            sparse_activations = activations[0]
            local_indices = sparse_activations.argsort(
                axis=-1)[:, -args.neighbours:]
            top_prods = index2dArray(sparse_indices, local_indices)
        else:
            top_prods = activations.argsort(axis=-1)[:, -args.neighbours:]
        assert (top_prods.shape[0] == number_queries)
        for i in range(number_queries):
            for j in range(top_prods.shape[1]):
                if target_ids[i] == top_prods[i, j]:
                    continue
                adjacency_list[target_ids[i]].add(top_prods[i, j])
                if args.undirected_edges:
                    adjacency_list[top_prods[i, j]].add(target_ids[i])
    return adjacency_list


def get_adj_list_from_faiss(args):
    # We expect to have the following parameters in args
    # 1. embed_path
    # 2. threshold
    # 3. neighbours
    # 4. undirected_edges
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

    adj = defaultdict(set)
    for u in tqdm(range(nb)):
        for j in range(k):
            v = int(indices[u, j])
            # No self loops, distance has to be within something.
            if v != u and distances[u, j] < args.threshold:
                adj[u].add(v)
                if args.undirected_edges:
                    adj[v].add(u)
    return adj


def generate_adj_list(args):
    indexer = args.indexer
    if indexer == "model":
        return get_adj_list_from_model(args)

    if indexer == "faiss":
        return get_adj_list_from_faiss(args)
