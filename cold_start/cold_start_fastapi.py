import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, FileResponse
from thirdai import bolt
import os
from starlette.staticfiles import StaticFiles
from argparse import Namespace
import json


def init():
    config_path = os.environ["config_path"]
    with open(config_path, "r") as f:
        config_data = json.load(f)
        args = Namespace(**config_data)

    network = bolt.UniversalDeepTransformer.load(args.model_path)
    df = pd.read_csv(args.catalog_path)

    df = df[args.strong_column_names + [args.target_name]]

    for column in args.strong_column_names:
        df[column] = df[column].fillna(f"missing value for {column} entry")

    return network, df, args


network, df, args = init()
print(args)
app = FastAPI()

router = APIRouter(prefix=args.api_prefix)

# Allowing cross-origin requests for demo-purposes. This allows the single-page
# app to communicate with the API backend without getting 404s.
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def top_k_products(query: str, top_k: int):
    query = ' '.join([query[i:i+4] for i in range(len(query)-3)])
    result = network.predict({args.query_column_name: query})
    #
    k = min(top_k, len(result) - 1)
    sorted_product_ids = result.argsort()[-k:][::-1]
    ls = []
    for p_id in sorted_product_ids:
        ls.append(dict(df.iloc[p_id]))
    return ls


def serialize(x):
    if isinstance(x, list):
        for i, elements in enumerate(x):
            x[i] = serialize(elements)
        return x

    if isinstance(x, tuple):
        x = list(x)
        return serialize(x)

    if isinstance(x, np.ndarray):
        return x.tolist()

    if isinstance(x, dict):
        y = {}
        for key, value in x.items():
            y[key] = serialize(value)
        return y

    return str(x)


@router.get("/predict")
async def predict(query: str, k: int):
    try:
        results = top_k_products(query, k)
        print(results)
        result = serialize(results)
        status = "Success"
        message = "Success"

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        result = ""
        status = "Failed"

    return {"Result": result, "Status": status, "Message": message}


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, "..", "data")
GALAXY_DIR = os.path.join(ROOT_DIR, "..", "galaxy/build")

print(os.path.join(GALAXY_DIR, "index.html"))


app.include_router(router)


app.mount(f"{args.api_prefix}/data",
          StaticFiles(directory=DATA_DIR, html=True), name="data")

app.mount(f"{args.api_prefix}", StaticFiles(directory=GALAXY_DIR,
          html=True), name="frontend")
