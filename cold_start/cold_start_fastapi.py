import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from thirdai import bolt
import os

app = FastAPI()
router = APIRouter()

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

network = bolt.UniversalDeepTransformer.load(os.environ["MODEL_PATH"])
dataframe = pd.read_csv(os.environ["CATALOG_PATH"])

# Use only few entries.
df = dataframe.iloc[:, [0, 1, 2]]

# Empty description causes JSON encode-decode errors. We simply replace it
# with (empty).
df["DESCRIPTION"] = df["DESCRIPTION"].fillna("(empty)")


def top_k_products(query: str, top_k: int):
    result = network.predict({"QUERY": query})
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


@router.get("/")
async def homepage(request: Request):
    return HTMLResponse("<p>Make api calls to /predict for inference requests. <\/p>")


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


api_prefix = os.environ.get("API_PREFIX", "/")
app.include_router(router, prefix=api_prefix)
